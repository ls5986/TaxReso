import re
import pandas as pd
from typing import Dict, List, Union
from utils.tax_utils import create_tax_projection
from utils.common import get_last_four_ssn, extract_float

def create_client_summary(results):
    summary_data = {}
    for result in results:
        year = result['Tax Period']
        if year.isdigit() and len(year) == 4:
            tax_year = year
        else:
            year_match = re.search(r'\d{4}', year)
            tax_year = year_match.group() if year_match else 'Unknown'
        
        ssn = result['SSN']
        last_four_ssn = get_last_four_ssn(ssn)
        key = (last_four_ssn, tax_year)
        
        if key not in summary_data:
            summary_data[key] = {
                'SSN Last Four': last_four_ssn,
                'Tax Year': tax_year,
                'Return Filed': 'No',
                'Filing Status': 'Unknown',
                'Current Balance': 0,
                'Balance Plus Accruals': 0,
                'CSED Date': 'Unknown',
                'Legal Action': 'Unknown',
                'Projected Amount Owed': 0,
                'Income Types': 'Unknown',
            }
        
        if result['Transcript Type'] in ["Account Transcript", "Record of Account"]:
            summary_data[key]['Return Filed'] = 'Yes' if result['Return Filed'] else 'No'
            summary_data[key]['Filing Status'] = result['Income'].get('FILING STATUS', 'Unknown')
            
            # Assign Current Balance
            current_balance = 0.0
            for detail in result['Details']:
                if 'Current Balance' in detail:
                    current_balance = extract_float(detail['Current Balance'])
                    break
            summary_data[key]['Current Balance'] = current_balance

            # Assign Balance Plus Accruals separately
            balance_plus_accruals = 0.0
            for detail in result['Details']:
                if '(this is not a payoff amount)' in detail:
                    balance_plus_accruals = extract_float(detail['(this is not a payoff amount)'])
                    break
            summary_data[key]['Balance Plus Accruals'] = balance_plus_accruals
            
            summary_data[key]['Adjusted Gross Income'] = extract_float(result['Income'].get('ADJUSTED GROSS INCOME', '0'))
            summary_data[key]['Taxable Income'] = extract_float(result['Income'].get('TAXABLE INCOME', '0'))
            summary_data[key]['Tax Per Return'] = extract_float(result['Income'].get('TAX PER RETURN', '0'))
        
        # Update Projected Amount Owed only for unfiled returns
        if result['Return Filed'] == 'No':  # Only apply to unfiled years
            projection = create_tax_projection(result, 1, 'Unknown', 'Unknown')
            summary_data[key]['Projected Amount Owed'] = projection['Projected Amount Owed']
    
    df = pd.DataFrame(summary_data.values())
    df['Current Balance'] = df['Current Balance'].apply(lambda x: f'${x:.2f}')
    df['Balance Plus Accruals'] = df['Balance Plus Accruals'].apply(lambda x: f'${x:.2f}')
    df['Adjusted Gross Income'] = df['Adjusted Gross Income'].apply(lambda x: f'${x:.2f}')
    df['Taxable Income'] = df['Taxable Income'].apply(lambda x: f'${x:.2f}')
    df['Tax Per Return'] = df['Tax Per Return'].apply(lambda x: f'${x:.2f}')
    df['Projected Amount Owed'] = df['Projected Amount Owed'].apply(lambda x: f'${x:.2f}')
    
    return df
