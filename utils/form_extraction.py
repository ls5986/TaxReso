# utils/form_extraction.py
from utils.form_definitions import form_income_withholdings

def extract_income_withholdings(form_type, form_data):
    income_withholdings = form_income_withholdings.get(form_type, {})
    extracted_data = {
        'Income': {},
        'Withholdings': {}
    }

    for income_field in income_withholdings.get('Income', []):
        if income_field in form_data:
            extracted_data['Income'][income_field] = form_data[income_field]

    for withholding_field in income_withholdings.get('Withholdings', []):
        if withholding_field in form_data:
            extracted_data['Withholdings'][withholding_field] = form_data[withholding_field]

    return extracted_data
