import streamlit as st
import io
import PyPDF2
import pandas as pd
import re
import base64
import requests
from typing import Dict, List, Union

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def extract_float(value: str) -> float:
    try:
        return float(value.replace(',', '').replace('$', ''))
    except ValueError:
        return 0.0


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

def parse_transcript(content: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
    lines = content.split('\n')
    
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


def get_last_four_ssn(ssn: str) -> str:
    return ssn[-4:] if len(ssn) >= 4 else "Unknown"

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
            'CSED Date': 'Unknown',
            'Legal Action': 'Unknown',
            'Projected Balance': 0,
            'Income Types': 'Unknown',
            }
        
        if result['Transcript Type'] in ["Account Transcript", "Record of Account"]:
            summary_data[key]['Return Filed'] = 'Yes' if result['Return Filed'] else 'No'
            summary_data[key]['Filing Status'] = result['Income'].get('FILING STATUS', 'Unknown')
            
            balance_plus_accruals = 0.0
            for detail in result['Details']:
                if '(this is not a payoff amount)' in detail:
                    balance_plus_accruals = float(detail['(this is not a payoff amount)'].replace(',', ''))
                    break
            summary_data[key]['Balance Plus Accruals'] = balance_plus_accruals
            summary_data[key]['Adjusted Gross Income'] = extract_float(result['Income'].get('ADJUSTED GROSS INCOME', '0'))
            summary_data[key]['Taxable Income'] = extract_float(result['Income'].get('TAXABLE INCOME', '0'))
            summary_data[key]['Tax Per Return'] = extract_float(result['Income'].get('TAX PER RETURN', '0'))
        
        if result['Return Filed'] == False:
            projection = create_tax_projection(result, 1, 'Unknown', 'Unknown')
            summary_data[key]['Projected Amount Owed'] = projection['Projected Amount Owed']
    
    df = pd.DataFrame(summary_data.values())
    df['Balance Plus Accruals'] = df['Balance Plus Accruals'].apply(lambda x: f'${x:.2f}')
    df['Adjusted Gross Income'] = df['Adjusted Gross Income'].apply(lambda x: f'${x:.2f}')
    df['Taxable Income'] = df['Taxable Income'].apply(lambda x: f'${x:.2f}')
    df['Tax Per Return'] = df['Tax Per Return'].apply(lambda x: f'${x:.2f}')
    df['Projected Amount Owed'] = df['Projected Amount Owed'].apply(lambda x: f'${x:.2f}')
    return df

def display_pdf(file):
    bytes_data = file.getvalue()
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def process_transcripts(transcripts: List[str]) -> List[Dict[str, Union[str, Dict]]]:
    results = []
    for content in transcripts:
        parsed_data = parse_transcript(content)
        results.append(parsed_data)
    return results

def highlight_not_filed(row):
    color = 'red' if row['Return Filed'] == 'No' else ''
    return ['background-color: {}'.format(color) for _ in row]

def main():
    st.set_page_config(layout="wide")
    st.title("Tax Transcript Parser")
    st.write("Upload your tax transcript files (PDF or TXT) and see the parsed results.")

    uploaded_files = st.file_uploader("Choose tax transcript files", accept_multiple_files=True, type=['pdf', 'txt'])

    household_size = st.number_input("Household Size", min_value=1, value=1)

    # Load US states and counties from GitHub JSON file
    states_url = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/refs/heads/master/json/states.json'
    counties_url = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/refs/heads/master/json/cities.json'

    states_response = requests.get(states_url)

    if states_response.status_code == 200:
        states = [state for state in states_response.json() if state['country_code'] == 'US']
        state_names = [state['name'] for state in states]
        state_code_map = {state['name']: state['id'] for state in states}
        
        state = st.selectbox("State", state_names)
        
        selected_state_id = state_code_map[state]
        counties_response = requests.get(counties_url)
        
        if counties_response.status_code == 200:
            counties = [county for county in counties_response.json() if county['state_id'] == selected_state_id]
            county_names = [county['name'] for county in counties]
            county = st.selectbox("County", county_names)
        else:
            st.error("Failed to load counties. Please try again later.")
    else:
        st.error("Failed to load states. Please try again later.")

    if uploaded_files:
        all_transcripts = []
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                text_content = extract_text_from_pdf(uploaded_file)
            else:
                text_content = uploaded_file.getvalue().decode("utf-8")
            all_transcripts.append(text_content)

        results = process_transcripts(all_transcripts)

        st.header("Client Summary")
        client_summary = create_client_summary(results)

        unique_ssn_last_four = client_summary['SSN Last Four'].unique()
        selected_ssn_last_four = st.selectbox("Select a client (Last 4 digits of SSN):", unique_ssn_last_four)

        selected_client_summary = client_summary[client_summary['SSN Last Four'] == selected_ssn_last_four]

        # Apply conditional formatting to the DataFrame to highlight rows where the return is not filed
        styled_df = selected_client_summary.style.apply(highlight_not_filed, axis=1)

        # Display the styled DataFrame
        st.dataframe(styled_df, use_container_width=True)

        # Calculate total tax liability only for filed returns
        total_liability = selected_client_summary[selected_client_summary['Return Filed'] == 'Yes']['Tax Per Return']
        total_liability_sum = total_liability.apply(lambda x: float(x.replace('$', '').replace(',', ''))).sum()

        # Calculate total projected amount owed for unfiled returns
        total_projected = selected_client_summary[selected_client_summary['Return Filed'] == 'No']['Projected Amount Owed']
        total_projected_sum = total_projected.apply(lambda x: float(x.replace('$', '').replace(',', ''))).sum()

        st.write(f"Total Tax Liability for selected client: ${total_liability_sum:.2f}")
        st.write(f"Total Projected Amount Owed for Unfiled Returns: ${total_projected_sum:.2f}")

        csv = selected_client_summary.to_csv(index=False)
        st.download_button(
            label="Download Selected Client Summary as CSV",
            data=csv,
            file_name=f"client_summary_{selected_ssn_last_four}.csv",
            mime="text/csv",
        )

        st.header("Detailed Document View")
        st.write("Expand the sections below to view details of individual documents.")

        selected_client_results = [result for result in results if get_last_four_ssn(result['SSN']) == selected_ssn_last_four]
        selected_client_files = [file for file, result in zip(uploaded_files, results) if get_last_four_ssn(result['SSN']) == selected_ssn_last_four]

        for i, (result, uploaded_file) in enumerate(zip(selected_client_results, selected_client_files)):
            with st.expander(f"Document {i + 1}: {uploaded_file.name}"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write(f"Transcript Type: {result['Transcript Type']}")
                    st.write(f"Tracking Number: {result['Tracking Number']}")
                    st.write(f"Tax Period: {result['Tax Period']}")
                    st.write(f"SSN: {result['SSN']}")
                    st.write(f"Return Filed: {'Yes' if result['Return Filed'] else 'No'}")
                    
                    st.write("Income and Details:")
                    if result['Transcript Type'] in ["Account Transcript", "Record of Account", "Wage and Income Summary"]:
                        df = pd.DataFrame.from_dict(result['Income'], orient='index', columns=['Value'])
                        df.index.name = 'Field'
                        st.dataframe(df)
                    else:
                        for form, income_data in result['Income'].items():
                            st.write(f"{form}:")
                            flat_data = flatten_dict(income_data)
                            df = pd.DataFrame.from_dict(flat_data, orient='index', columns=['Value'])
                            df.index.name = 'Field'
                            st.dataframe(df)

                    if not result['Return Filed']:
                        st.write("Tax Projection:")
                        projection = create_tax_projection(result, household_size, county, state)
                        st.write(f"Projected Amount Owed: ${projection['Projected Amount Owed']:.2f}")
                
                with col2:
                    st.write("Original Document:")
                    if uploaded_file.type == "application/pdf":
                        display_pdf(uploaded_file)
                    else:
                        st.text(uploaded_file.getvalue().decode("utf-8"))

if __name__ == "__main__":
    main()
