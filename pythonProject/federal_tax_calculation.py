def calculate_federal_tax(income, ltcg=0):
    # brackets for 2025 Married Filing Jointly
    brackets = [
        (0, 23850, 0.10),
        (23850, 96950, 0.12),
        (96950, 206700, 0.22),
        (206700, 394600, 0.24),
        (394600, 501050, 0.32),
        (501050, 751600, 0.35),
        (751600, float('inf'), 0.37)
    ]

    # LTCG tax brackets for MFJ (2025)
    ltcg_brackets = [
        (0, 89250, 0.0),
        (89250, 553850, 0.15),
        (553850, float('inf'), 0.20)
    ]

    total_income = income + ltcg

    tax_breakdown = []
    # Calculate ordinary income tax
    ordinary_tax = 0
    for lower, upper, rate in brackets:
        if income > lower:
            taxable_amount = min(income, upper) - lower
            tax = taxable_amount * rate
            ordinary_tax += tax
            tax_breakdown.append((lower, upper, rate, taxable_amount, tax))
            if income <= upper:
                break

    # Calculate LTCG tax
    ltcg_tax = 0
    remaining_ltcg = ltcg
    for low, high, rate in ltcg_brackets:
        if total_income > low:
            taxed = min(total_income, high) - low
            taxable_ltcg = min(taxed, remaining_ltcg)
            ltcg_tax += taxable_ltcg * rate
            remaining_ltcg -= taxable_ltcg
            if remaining_ltcg <= 0:
                break

    return ordinary_tax + ltcg_tax, ordinary_tax, ltcg_tax, tax_breakdown


def calculate_taxable_ss(agi_ex_ss, ss_benefits):
    provisional = agi_ex_ss + 0.5 * ss_benefits
    # Thresholds for 2025 married filing jointly
    t1, t2 = 32_000, 44_000
    if provisional <= t1:
        taxed_ss = 0
    elif provisional <= t2:
        taxed_ss = min(0.5 * ss_benefits, 0.5 * (provisional - t1))
    else:
        part1 = min(0.5 * ss_benefits, 0.5 * (t2 - t1))
        part2 = min(0.85 * ss_benefits, 0.35 * (provisional - t2))
        taxed_ss = part1 + part2
    percent_taxed = taxed_ss / ss_benefits * 100 if ss_benefits > 0 else 0
    return provisional, taxed_ss, percent_taxed

def calculate_arizona_tax(federal_agi, filing_status='married_joint'):
    # Arizona standard deductions for 2024 (to be used for 2025 filing)
    standard_deductions = {
        'single': 14600,
        'married_joint': 30000,
        'married_separate': 14600,
        'head_of_household': 21900
    }

    # Get the standard deduction based on filing status
    standard_deduction = standard_deductions.get(filing_status, 0)
    # Calculate Arizona taxable income
    arizona_taxable_income = max(0, federal_agi - standard_deduction)
    # Arizona flat tax rate
    tax_rate = 0.025
    # Calculate tax owed
    az_tax_owed = arizona_taxable_income * tax_rate

    return az_tax_owed

def calculate_all(total_income, ss_benefits, ltcg):
    # Apply standard deduction for married couple both over 65
    STANDARD_DEDUCTION = 30000 + (2 * 1600) + (2 * 6000) # 2025 values
    agi_ex_ss = max(0, total_income - STANDARD_DEDUCTION)
    provisional, taxed_ss, pct = calculate_taxable_ss(agi_ex_ss, ss_benefits)
    agi = agi_ex_ss + taxed_ss
    total_tax, ordinary_tax, ltcg_tax, tax_breakdown = calculate_federal_tax(agi, ltcg)
    state_tax = calculate_arizona_tax(agi + ltcg)

    print('\n')

    for lower, upper, rate, taxable, tax in tax_breakdown:
        print(f"Taxable income of ${taxable:,.0f} in the range from ${lower:,.0f} to ${upper:,.0f} taxed at {rate * 100:.0f}%: ${tax:,.2f}")

    return {
        'provisional_income': provisional,
        'taxable_ss': taxed_ss,
        'percent_ss_taxed': pct,
        'federal_ag_user': agi,
        'federal_tax_owed': total_tax,
        'state_tax_owed': state_tax,
        'ordinary_tax': ordinary_tax,
        'ltcg_tax': ltcg_tax
    }

if __name__ == "__main__":
    tot = float(input("Enter your total non‑Social Security income for the year: "))
    ss = float(input("Enter your total Social Security benefits: "))
    ltcg = float(input("Enter your long-term capital gains: "))
    res = calculate_all(tot, ss, ltcg)

    print(f"Provisional Income: ${res['provisional_income']:.2f}")
    print(f"Taxable SS Benefits: ${res['taxable_ss']:.2f}")
    print(f"Percent of SS taxed: {res['percent_ss_taxed']:.1f}%")
    print(f"Federal AGI (incl. taxable SS & LTCG): ${res['federal_ag_user']:.2f}")
    print(f"Federal Tax Owed (2025 brackets): ${res['federal_tax_owed']:.2f}")
    print(f"  - Ordinary Income Tax: ${res['ordinary_tax']:.2f}")
    print(f"  - Long-Term Capital Gains Tax: ${res['ltcg_tax']:.2f}")
    print(f"AZ State Tax Owed (2025 brackets): ${res['state_tax_owed']:.2f}")

