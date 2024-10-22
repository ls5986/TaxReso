import re
from typing import Dict, List, Union

def parse_transcript(content: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
    lines = content.split('\n')  # Correct indentation
    
    if "Account Transcript" in content:
        transcript_type = "Account Transcript"
    elif "Record of Account" in content:
        transcript_type = "Record of Account"
    elif "Wage and Income Transcript" in content:
        if "Wage & Income Summary" in content and not any(form in content for form in ['W-2', '1099-MISC', '1099-NEC', '1099-G', '1099-DIV']):
            transcript_type = "Wage and Income Summary"
        else:
            transcript_type = "Wage and Income Transcript"
    else:
        transcript_type = "Unknown"
    
    data = {
        "Transcript Type": transcript_type,
        "Tracking Number": "",
        "Tax Period": "",
        "SSN": "",
        "Details": [],
        "Income": {},
        "Return Filed": False  # Default is False, will update if Code:150 is found
    }
    
    tracking_number_pattern = re.compile(r'Tracking Number[:\s]*([\d]+)')
    tax_period_pattern = re.compile(r'Tax Period[:\s]*([\d-]+)|TAX PERIOD[:\s]*([A-Za-z\s\d.,]+)|Tax Period Requested[:\s]*([A-Za-z\s\d.,]+)')
    ssn_pattern = re.compile(r'SSN Provided[:\s]*([\d-]+)|TAXPAYER IDENTIFICATION NUMBER[:\s]*([\d-]+|XXX-XX-\d{4})')
    form_pattern = re.compile(r'Form\s+([\w-]+)')
    
    current_form = None
    
    income_fields = {
        'W-2': ['Wages, Tips and Other Compensation'],
        '1099-MISC': ['Non-Employee Compensation', 'Medical Payments', 'Fishing Income', 'Rents', 'Royalties', 'Attorney Fees', 'Other Income', 'Substitute Payments for Dividends'],
        '1099-NEC': ['Non-Employee Compensation'],
        '1099-K': ['Gross Amount of Payment Card/Third Party Transactions'],
        '1099-PATR': ['Patronage Dividends', 'Non-Patronage Distribution', 'Retained Allocations', 'Redemption Amount'],
        '1042-S': ['Gross Income'],
        'K-1 1065': ['Royalties', 'Ordinary Income K-1', 'Real Estate', 'Other Rental', 'Guaranteed Payments', 'Dividends', 'Interest'],
        'K-1 1041': ['Net Rental Real Estate Income', 'Other Rental Income', 'Dividends', 'Interest', 'Long-Term Capital Gain', 'Other Portfolio and Non-Business Income'],
        'W-2G': ['Gross Winnings'],
        '1099-R': ['Taxable Amount'],
        '1099-B': ['Proceeds', 'Cost or Basis'],
        '1099-S': ['Gross Proceeds'],
        '1099-LTC': ['Gross Long-Term Care Benefits Paid', 'Accelerated Death Benefits Paid'],
        '3922': ['Exercise Fair Market Value per Share on Exercise Date', 'Exercise Price per Share', 'Number of Shares Transferred'],
        'K-1 1120S': ['Dividends', 'Interest', 'Royalties', 'Ordinary Income K-1', 'Real Estate', 'Other Rental'],
        'SSA': ['Pensions and Annuities (Total Benefits Paid)'],
        '1099-DIV': ['Qualified Dividends', 'Cash Liquidation Distribution', 'Capital Gains', 'Ordinary Dividend'],
        '1099-INT': ['Interest'],
        '1099-G': ['Unemployment Compensation', 'Agricultural Subsidies', 'Taxable Grants'],
        '1098': ['Mortgage Interest Received from Payer(s)/Borrower(s)', 'Outstanding Mortgage Principle']
    }
    withholding_fields = {
        'W-2': ['Federal Income Tax Withheld'],
        '1099-MISC': ['Tax Withheld'],
        '1099-NEC': ['Federal Income Tax Withheld'],
        '1099-K': ['Federal Income Tax Withheld'],
        '1099-PATR': ['Tax Withheld'],
        '1042-S': ['U.S. Federal Tax Withheld'],
        'W-2G': ['Federal Income Tax Withheld'],
        '1099-R': ['Tax Withheld'],
        'SSA': ['Tax Withheld'],
        '1099-DIV': ['Tax Withheld'],
        '1099-INT': ['Tax Withheld'],
        '1099-G': ['Tax Withheld']
    }
    
    for line in lines:
        tracking_number_match = tracking_number_pattern.search(line)
        if tracking_number_match:
            data["Tracking Number"] = tracking_number_match.group(1)
            
        tax_period_match = tax_period_pattern.search(line)
        if tax_period_match:
            tax_period_value = tax_period_match.group(1) or tax_period_match.group(2) or tax_period_match.group(3)
            if tax_period_value:
                year_match = re.search(r'\d{4}', tax_period_value)
                if year_match:
                    data["Tax Period"] = year_match.group()
                else:
                    data["Tax Period"] = "Unknown"
        
        ssn_match = ssn_pattern.search(line)
        if ssn_match:
            data["SSN"] = ssn_match.group(1) if ssn_match.group(1) else ssn_match.group(2)
        
        # Check if Code:150 is present, indicating the return has been filed
        if '150' in line:
            data["Return Filed"] = True
        
        form_match = form_pattern.search(line)
        if form_match:
            current_form = form_match.group(1)
            if current_form not in data["Income"]:
                data["Income"][current_form] = {"Income": {}, "Withholdings": {}}
        
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                data["Details"].append({key: value})
                if transcript_type in ["Account Transcript", "Record of Account"]:
                    data["Income"][key] = value
                elif transcript_type == "Wage and Income Transcript" and current_form:
                    if key in income_fields.get(current_form, []):
                        data["Income"][current_form]["Income"][key] = value
                    elif key in withholding_fields.get(current_form, []):
                        data["Income"][current_form]["Withholdings"][key] = value
                elif transcript_type == "Wage and Income Summary":
                    data["Income"][key] = value
    return data

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
    
def process_transcripts(transcripts: List[str]) -> List[Dict[str, Union[str, Dict]]]:
    results = []
    for content in transcripts:
        parsed_data = parse_transcript(content)
        results.append(parsed_data)
    return results
