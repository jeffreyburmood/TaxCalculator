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


# Example usage:
income = float(input("Enter your taxable income: "))
total_tax, breakdown = calculate_federal_tax(income)

print(f"Total Federal Tax Owed: ${total_tax:,.2f}")
print("Breakdown:")
for lower, upper, rate, taxable, tax in breakdown:
    print(f"Income from ${lower:,.0f} to ${upper:,.0f} taxed at {rate * 100:.0f}%: ${tax:,.2f}")
