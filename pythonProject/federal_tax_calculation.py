""" this file contains methods used to calculate federal and state tax estimates for a given tax year """

class NoMatchFoundError(Exception):
    """Raised when no condition in the decision chain matches."""
    pass

class TaxTables():
    def __init__(self, year):
        self.year = year
        self.federal_brackets = []
        self.ltcg_brackets = []
        self.federal_std_deduction = float(0)
        self.federal_over_65_deduction = float(0)
        self.federal_over_65_extra_deduction = float(0)
        self.arizona_tax_rate = float(0)
        self.ss_thresholds = (float(0), float(0), float(0))

    def get_federal_brackets(self):

        if self.year == '2025':
            self.federal_brackets = [
                (0, 23850, 0.10),  # (0, 24800)
                (23850, 96950, 0.12),  # (24801, 100800)
                (96950, 206700, 0.22),  # (100801, 211400)
                (206700, 394600, 0.24),  # (211401, 403550)
                (394600, 501050, 0.32),  # (403551, 512450)
                (501050, 751600, 0.35),  # (512451, 768700)
                (751600, float('inf'), 0.37)  # (76701, +)
            ]
        elif self.year == '2026':
            self.federal_brackets = [
                (0, 24800, 0.10),  # (0, 24800)
                (24800, 100800, 0.12),  # (24801, 100800)
                (100800, 211400, 0.22),  # (100801, 211400)
                (211400, 403550, 0.24),  # (211401, 403550)
                (403550, 512450, 0.32),  # (403551, 512450)
                (512450, 768700, 0.35),  # (512451, 768700)
                (768700, float('inf'), 0.37)  # (76701, +)
            ]
        else:
            # No match found in the if/elif chain
            raise NoMatchFoundError(f"Unrecognized tax year: {self.year}")

        return self.federal_brackets

    def get_ltcg_brackets(self):

        if self.year == '2025':
            self.ltcg_brackets = [
                (0, 89250, 0.0),  # (0, 98900, 0)
                (89250, 553850, 0.15),  # (98901, 613700, 15)
                (553850, float('inf'), 0.20)  # (613701, +, 20)
            ]
        elif self.year == '2026':
            self.ltcg_brackets = [
                (0, 98900, 0.0),  # (0, 98900, 0)
                (98901, 613700, 0.15),  # (98901, 613700, 15)
                (613701, float('inf'), 0.20)  # (613701, +, 20)
            ]
        else:
            # No match found in the if/elif chain
            raise NoMatchFoundError(f"Unrecognized tax year: {self.year}")

        return self.ltcg_brackets

    def get_federal_std_deduction(self):
        if self.year == '2025':
            self.federal_std_deduction = float(31500)
        elif self.year == '2026':
            self.federal_std_deduction = float(32200)
        else:
            # No match found in the if/elif chain
            raise NoMatchFoundError(f"Unrecognized tax year: {self.year}")

        return self.federal_std_deduction


    def get_arizona_tax_rate(self):
        if self.year == '2025':
            self.arizona_tax_rate = float(0.025)
        elif self.year == '2026':
            self.arizona_tax_rate = float(0.025)
        else:
            # No match found in the if/elif chain
            raise NoMatchFoundError(f"Unrecognized tax year: {self.year}")

        return self.arizona_tax_rate

    def get_federal_over_65_deduction(self):
        if self.year == '2025':
            self.federal_over_65_deduction = float(1600)
        elif self.year == '2026':
            self.federal_over_65_deduction = float(1650)
        else:
            # No match found in the if/elif chain
            raise NoMatchFoundError(f"Unrecognized tax year: {self.year}")

        return self.federal_over_65_deduction

    def get_federal_over_65_extra_deduction(self):
        if self.year == '2025':
            self.federal_over_65_extra_deduction = float(6000)
        elif self.year == '2026':
            self.federal_over_65_extra_deduction = float(6000)
        else:
            # No match found in the if/elif chain
            raise NoMatchFoundError(f"Unrecognized tax year: {self.year}")

        return self.federal_over_65_extra_deduction

    def get_ss_thresholds(self):
        if self.year == '2025':
            self.ss_thresholds = (float(32000), float(44000), float(0.85))
        elif self.year == '2026':
            self.ss_thresholds = (float(32000), float(44000), float(0.85))
        else:
            # No match found in the if/elif chain
            raise NoMatchFoundError(f"Unrecognized tax year: {self.year}")

        return self.ss_thresholds

def calculate_federal_tax(income, ltcg, tax_tables):
    # brackets for 2025 Married Filing Jointly
    brackets = tax_tables.get_federal_brackets()

    # LTCG tax brackets for MFJ (2025)
    ltcg_brackets = tax_tables.get_ltcg_brackets()

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


def calculate_taxable_ss(total_income, ss_benefits, tax_tables):
    """
    Calculate provisional income and taxable Social Security benefits
    for a Married Filing Jointly couple using standard IRS rules.

    Parameters
    ----------
    non_ss_income : float
        All non–Social Security income that goes into provisional income
        (wages, pensions, IRA distributions, interest, etc.).
        Assumes no tax-exempt interest for simplicity. Add that in if needed.
    ss_benefits : float
        Total Social Security benefits received during the year.

    Returns
    -------
    provisional_income : float
        Provisional income used to determine taxable Social Security.
    taxable_ss : float
        Amount of Social Security benefits that is taxable.
    percent_taxable : float
        Percentage of Social Security benefits that is taxable (0–100).
    """
    provisional = total_income + 0.5 * ss_benefits
    # Thresholds for 2025 married filing jointly
    t1, t2, max_rate = tax_tables.get_ss_thresholds()
    if provisional <= t1:
        taxed_ss = 0
    elif provisional <= t2:
        taxed_ss = min(0.5 * ss_benefits, 0.5 * (provisional - t1))
    else:
        #part1 = min(0.5 * ss_benefits, (t2 - t1))
        #part2 = min(0.85 * ss_benefits, 0.35 * (provisional - t2))
        #taxed_ss = part1 + part2

        smaller_of_50pct = min(0.5 * ss_benefits, 6_000.0)
        option1 = 0.85 * (provisional - t2) + smaller_of_50pct
        option2 = max_rate * ss_benefits

        taxed_ss = min(option1, option2)

    if ss_benefits > 0:
        percent_taxed = (taxed_ss / ss_benefits) * 100.0
    else:
        percent_taxed = 0.0

    return provisional, taxed_ss, percent_taxed

def calculate_arizona_tax(federal_agi, tax_tables):

    standard_deduction = tax_tables.get_federal_std_deduction()
    # Calculate Arizona taxable income
    arizona_taxable_income = max(0, federal_agi)
    # Arizona flat tax rate
    tax_rate = tax_tables.get_arizona_tax_rate()
    # Calculate tax owed
    az_tax_owed = arizona_taxable_income * tax_rate

    return az_tax_owed

def calculate_all(total_non_ss_income, ss_benefits, ltcg, tax_year):
    tax_tables = TaxTables(tax_year)
    # Apply standard deduction for married couple both over 65
    # standard_deduction = 30000 + (2 * 1600) + (2 * 6000) # 2 * 2050 for 2026 - same 2 * 6000 for 2026
    standard_deduction = tax_tables.get_federal_std_deduction() + (2 * tax_tables.get_federal_over_65_deduction()) + (2 * tax_tables.get_federal_over_65_extra_deduction())
    provisional_income, taxed_ss, pct = calculate_taxable_ss(total_non_ss_income, ss_benefits, tax_tables)
    agi = max(0, provisional_income - standard_deduction)
    total_tax, ordinary_tax, ltcg_tax, tax_breakdown = calculate_federal_tax(agi, ltcg, tax_tables)
    state_tax = calculate_arizona_tax(agi + ltcg, tax_tables)

    print('\n')

    for lower, upper, rate, taxable, tax in tax_breakdown:
        print(f"Taxable income of ${taxable:,.0f} in the range from ${lower:,.0f} to ${upper:,.0f} taxed at {rate * 100:.0f}%: ${tax:,.2f}")

    return {
        'provisional_income': provisional_income,
        'taxable_ss': taxed_ss,
        'percent_ss_taxed': pct,
        'federal_ag_user': agi,
        'federal_tax_owed': total_tax,
        'state_tax_owed': state_tax,
        'ordinary_tax': ordinary_tax,
        'ltcg_tax': ltcg_tax
    }

if __name__ == "__main__":
    tax_year = input("Enter the active tax year: ")
    tot = float(input("Enter your total non‑Social Security income for the year: "))
    ss = float(input("Enter your total Social Security benefits: "))
    ltcg = float(input("Enter your long-term capital gains: "))
    res = calculate_all(tot, ss, ltcg, tax_year)

    print(f"Provisional Income: ${res['provisional_income']:.2f}")
    print(f"Taxable SS Benefits: ${res['taxable_ss']:.2f}")
    print(f"Percent of SS taxed: {res['percent_ss_taxed']:.1f}%")
    print(f"Federal AGI (incl. taxable SS & LTCG): ${res['federal_ag_user']:.2f}")
    print(f"Federal Tax Owed (2025 brackets): ${res['federal_tax_owed']:.2f}")
    print(f"  - Ordinary Income Tax: ${res['ordinary_tax']:.2f}")
    print(f"  - Long-Term Capital Gains Tax: ${res['ltcg_tax']:.2f}")
    print(f"AZ State Tax Owed (2025 brackets): ${res['state_tax_owed']:.2f}")

