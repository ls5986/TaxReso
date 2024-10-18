import re
from typing import Dict, List, Union

def parse_transcript(content: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
    lines = content.split('\n')
    transcript_type = "Account Transcript" if "Account Transcript" in content else "Wage and Income Transcript"
    
    data = {
        "Transcript Type": transcript_type,
        "Tracking Number": "",
        "Tax Period": "",
        "SSN": "",
        "Details": [],
        "Income": {}
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
        'SSA': ['Pensions and Annuities'],
        '1099-DIV': ['Qualified Dividends', 'Cash Liquidation Distribution', 'Capital Gains', 'Ordinary Dividend'],
        '1099-INT': ['Interest'],
        '1099-G': ['Unemployment Compensation', 'Agricultural Subsidies', 'Taxable Grants']
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
                if re.match(r'^[A-Za-z]+, \d{4}$', tax_period_value):
                    data["Tax Period"] = re.sub(r',', ' 1,', tax_period_value)
                else:
                    data["Tax Period"] = tax_period_value
        
        ssn_match = ssn_pattern.search(line)
        if ssn_match:
            data["SSN"] = ssn_match.group(1) if ssn_match.group(1) else ssn_match.group(2)
        
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
                if transcript_type == "Account Transcript":
                    data["Income"][key] = value
                elif current_form:
                    if key in income_fields.get(current_form, []):
                        data["Income"][current_form]["Income"][key] = value
                    elif key in withholding_fields.get(current_form, []):
                        data["Income"][current_form]["Withholdings"][key] = value

    return data

def process_transcripts(transcripts: List[str]) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
    return [parse_transcript(transcript) for transcript in transcripts]

# Example usage
transcripts = [
    """Account Transcript
Request Date: 10-15-2024
Response Date: 10-15-2024
Tracking Number: 106750208996
TAX PERIOD: Dec. 31, 2018
TAXPAYER IDENTIFICATION NUMBER: XXX-XX-2171
ACCOUNT BALANCE: 0.00
ACCRUED INTEREST: 0.00 AS OF: Apr. 25, 2022
ACCRUED PENALTY: 0.00 AS OF: Apr. 25, 2022
ADJUSTED GROSS INCOME: 8,938.00
TAXABLE INCOME: 0.00
TAX PER RETURN: 0.00""",

    """Wage and Income Transcript
Request Date: 10-15-2024
Response Date: 10-15-2024
Tracking Number: 106747277314
SSN Provided: 469-92-7417
Tax Period Requested: December, 2018
Form W-2 Wage and Tax Statement
Wages, Tips and Other Compensation: $586.00
Federal Income Tax Withheld: $0.00
Form 1099-MISC
Non-Employee Compensation: $64,478.00
Tax Withheld: $0.00
Form 1099-DIV
Ordinary Dividend: $66.00
Qualified Dividends: $66.00
Tax Withheld: $0.00
Form 1099-G
Unemployment Compensation: $2,948.00
Tax Withheld: $0.00"""
]

results = process_transcripts(transcripts)
for result in results:
    print(f"Transcript Type: {result['Transcript Type']}")
    print(f"Tracking Number: {result['Tracking Number']}")
    print(f"Tax Period: {result['Tax Period']}")
    print(f"SSN: {result['SSN']}")
    print("Income and Details:")
    if result['Transcript Type'] == "Account Transcript":
        for key, value in result['Income'].items():
            print(f"  {key}: {value}")
    else:
        for form, income_data in result['Income'].items():
            print(f"  {form}:")
            if income_data.get("Income"):
                print("    Income:")
                for key, value in income_data["Income"].items():
                    print(f"      {key}: {value}")
            if income_data.get("Withholdings"):
                print("    Withholdings:")
                for key, value in income_data["Withholdings"].items():
                    print(f"      {key}: {value}")
    print("\n")