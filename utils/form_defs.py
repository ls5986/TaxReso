# utils/form_definitions.py

form_income_withholdings = {
    'W-2': {
        'Income': ['Wages, Tips, and Other Compensation'],
        'Withholdings': ['Federal Income Tax Withheld'],
    },
    '1099-MISC': {
        'Income': ['Non-Employee Compensation', 'Medical Payments', 'Fishing Income', 'Rents', 'Royalties', 'Attorney Fees', 'Other Income', 'Substitute Payments for Dividends'],
        'Withholdings': ['Tax Withheld'],
    },
    '1099-NEC': {
        'Income': ['Non-Employee Compensation'],
        'Withholdings': ['Federal Income Tax Withheld'],
    },
    '1099-K': {
        'Income': ['Gross Amount of Payment Card/Third Party Transactions'],
        'Withholdings': ['Federal Income Tax Withheld'],
    },
    # Add more form types following the same structure...
}

