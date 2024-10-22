# utils/form_calculations.py

def calculate_for_w2(data):
    # Logic for W-2
    return {"calculation": "W2 result"}

def calculate_for_1099(data):
    # Logic for 1099
    return {"calculation": "1099 result"}

def calculate_for_wage_and_income_summary(data):
    # Logic for Wage and Income Summary
    return {"calculation": "Wage and Income Summary result"}

def calculate_based_on_form(form_type, data):
    calculation_map = {
        "W-2": calculate_for_w2,
        "1099-MISC": calculate_for_1099,
        "Wage and Income Summary": calculate_for_wage_and_income_summary,
        # Add more form types here
    }

    if form_type in calculation_map:
        return calculation_map[form_type](data)
    else:
        return {"calculation": "Unknown form type"}
