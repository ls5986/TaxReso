import streamlit as st
import io
import PyPDF2
import pandas as pd
import re
import base64
import requests
from typing import Dict, List, Union
# utils/tax_utils.py
from utils.common import extract_float

# Rest of your functions


# utils/tax_utils.py
def get_irs_standards(household_size, county, state):
    standards = {
        "food_clothing_misc": 733 * household_size,
        "housing_utilities": 2110,
        "vehicle_ownership": 588,
        "vehicle_operating_cost": 308,
        "public_transportation": 217,
        "health_insurance": 68 * household_size,
        "prescriptions_copays": 55 * household_size,
    }
    return standards

def calculate_tax(total_income):
    if total_income <= 10000:
        return total_income * 0.10
    elif total_income <= 50000:
        return 1000 + (total_income - 10000) * 0.15
    else:
        return 7000 + (total_income - 50000) * 0.25
    

def create_tax_projection(parsed_data, household_size, county, state):
    projection = {
        "(TP) Income Subject to SE Tax": 0,
        "(TP) Income Not Subject to SE Tax": 0,
        "(TP) Withholding": 0,
    }
    
    se_income_forms = ['1099-MISC', '1099-NEC', '1099-K', '1099-PATR', '1042-S', 'K-1 1065', 'K-1 1041']
    
    for form, data in parsed_data['Income'].items():
        if isinstance(data, dict) and 'Income' in data:
            if form in se_income_forms:
                for key, value in data['Income'].items():
                    projection["(TP) Income Subject to SE Tax"] += extract_float(value)
            else:
                for key, value in data['Income'].items():
                    projection["(TP) Income Not Subject to SE Tax"] += extract_float(value)
            
            for key, value in data.get('Withholdings', {}).items():
                projection["(TP) Withholding"] += extract_float(value)
        elif form in ['ADJUSTED GROSS INCOME', 'TAXABLE INCOME']:
            projection["(TP) Income Not Subject to SE Tax"] += extract_float(data)
    
    total_income = projection["(TP) Income Subject to SE Tax"] + projection["(TP) Income Not Subject to SE Tax"]
    
    irs_standards = get_irs_standards(household_size, county, state)
    projected_tax = calculate_tax(total_income)
    
    projection["Total Income"] = total_income
    projection["IRS Standards"] = irs_standards
    projection["Projected Tax"] = projected_tax
    projection["Projected Amount Owed"] = max(0, projected_tax - projection["(TP) Withholding"])
    
    return projection
