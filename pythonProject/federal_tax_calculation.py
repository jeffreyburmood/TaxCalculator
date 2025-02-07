def calculate_federal_tax(income):
    brackets = [
        (0, 11000, 0.10),
        (11000, 44725, 0.12),
        (44725, 95375, 0.22),
        (95375, 182100, 0.24),
        (182100, 231250, 0.32),
        (231250, 578125, 0.35),
        (578125, float('inf'), 0.37)
    ]

    tax_owed = 0
    tax_breakdown = []

    for lower, upper, rate in brackets:
        if income > lower:
            taxable_amount = min(income, upper) - lower
            tax = taxable_amount * rate
            tax_owed += tax
            tax_breakdown.append((lower, upper, rate, taxable_amount, tax))
            if income <= upper:
                break

    return tax_owed, tax_breakdown

def calculate_arizona_tax(federal_agi, filing_status='married_joint'):
    # Arizona standard deductions for 2024 (to be used for 2025 filing)
    standard_deductions = {
        'single': 14600,
        'married_joint': 29200,
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
    tax_owed = arizona_taxable_income * tax_rate

    return tax_owed


# Adjust income for standard deduction
STANDARD_DEDUCTION = float(29200 + (2 * 1550))  # Married filing jointly, both 65+
income = float(input("Enter your total income before deductions: "))
federal_agi = max(0, income - STANDARD_DEDUCTION)  # Ensure income doesn't go negative

total_tax, breakdown = calculate_federal_tax(federal_agi)

print(f"Total Federal Tax Owed: ${total_tax:,.2f}")
print("Breakdown:")
for lower, upper, rate, taxable, tax in breakdown:
    print(f"Income from ${lower:,.0f} to ${upper:,.0f} taxed at {rate * 100:.0f}%: ${tax:,.2f}")

tax_owed = calculate_arizona_tax(federal_agi)
print(f"Arizona State Tax Owed: ${tax_owed:,.2f}")
