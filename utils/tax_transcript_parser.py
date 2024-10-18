import streamlit as st
import io
import PyPDF2
import pandas as pd
import re
import base64
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
                # Extract only the year from the tax period
                year_match = re.search(r'\d{4}', tax_period_value)
                if year_match:
                    data["Tax Period"] = year_match.group()
                else:
                    data["Tax Period"] = "Unknown"
        
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

def process_transcripts(transcripts: List[str]) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
    return [parse_transcript(transcript) for transcript in transcripts]

def extract_float(value):
    # Extract the first occurrence of a number (including decimal point)
    match = re.search(r'-?\d+(?:\.\d+)?', str(value))
    if match:
        return float(match.group())
    return 0.0

def get_last_four_ssn(ssn):
    return ssn[-4:]

def create_client_summary(results):
    summary_data = {}
    for result in results:
        year = result['Tax Period']
        # Ensure year is in correct format
        if year.isdigit() and len(year) == 4:
            tax_year = year
        else:
            # If year is not in correct format, try to extract it or use 'Unknown'
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
                'Balance Plus Accruals': 0,
                'Adjusted Gross Income': 0,
                'Taxable Income': 0,
                'Tax Per Return': 0,
                'W-2': 'No',
                '1099-MISC': 'No',
                '1099-NEC': 'No',
            }
        
        if result['Transcript Type'] in ["Account Transcript", "Record of Account"]:
            summary_data[key]['Return Filed'] = 'Yes'
            summary_data[key]['Filing Status'] = result['Income'].get('FILING STATUS', 'Unknown')
            account_balance = extract_float(result['Income'].get('ACCOUNT BALANCE', '0'))
            accrued_interest = extract_float(result['Income'].get('ACCRUED INTEREST', '0'))
            accrued_penalty = extract_float(result['Income'].get('ACCRUED PENALTY', '0'))
            summary_data[key]['Balance Plus Accruals'] = account_balance + accrued_interest + accrued_penalty
            summary_data[key]['Adjusted Gross Income'] = extract_float(result['Income'].get('ADJUSTED GROSS INCOME', '0'))
            summary_data[key]['Taxable Income'] = extract_float(result['Income'].get('TAXABLE INCOME', '0'))
            summary_data[key]['Tax Per Return'] = extract_float(result['Income'].get('TAX PER RETURN', '0'))
        
        if result['Transcript Type'] in ["Wage and Income Transcript", "Wage and Income Summary"]:
            if 'W-2' in result['Income'] or 'Wages, tips, other comp.' in result['Income']:
                summary_data[key]['W-2'] = 'Yes'
            if '1099-MISC' in result['Income'] or 'Nonemployee compensation' in result['Income']:
                summary_data[key]['1099-MISC'] = 'Yes'
            if '1099-NEC' in result['Income']:
                summary_data[key]['1099-NEC'] = 'Yes'
    
    df = pd.DataFrame(summary_data.values())
    df['Balance Plus Accruals'] = df['Balance Plus Accruals'].apply(lambda x: f'${x:.2f}')
    df['Adjusted Gross Income'] = df['Adjusted Gross Income'].apply(lambda x: f'${x:.2f}')
    df['Taxable Income'] = df['Taxable Income'].apply(lambda x: f'${x:.2f}')
    df['Tax Per Return'] = df['Tax Per Return'].apply(lambda x: f'${x:.2f}')
    return df

def display_pdf(file):
    # Read file as bytes
    bytes_data = file.getvalue()
    
    # Convert to base64
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    
    # Embed PDF viewer
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    
    # Display the PDF
    st.markdown(pdf_display, unsafe_allow_html=True)

def main():
    st.set_page_config(layout="wide")
    st.title("Tax Transcript Parser")
    st.write("Upload your tax transcript files (PDF or TXT) and see the parsed results.")

    uploaded_files = st.file_uploader("Choose tax transcript files", accept_multiple_files=True, type=['pdf', 'txt'])

    if uploaded_files:
        all_transcripts = []
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                text_content = extract_text_from_pdf(uploaded_file)
            else:
                text_content = uploaded_file.getvalue().decode("utf-8")
            all_transcripts.append(text_content)

        results = process_transcripts(all_transcripts)

        # Client Summary View
        st.header("Client Summary", divider='blue')
        client_summary = create_client_summary(results)

        # Get unique SSN last four digits for client selection
        unique_ssn_last_four = client_summary['SSN Last Four'].unique()
        selected_ssn_last_four = st.selectbox("Select a client (Last 4 digits of SSN):", unique_ssn_last_four)

        # Filter summary for selected client
        selected_client_summary = client_summary[client_summary['SSN Last Four'] == selected_ssn_last_four]

        # Display selected client summary
        st.dataframe(selected_client_summary, use_container_width=True)

        # Calculate and display total tax liability
        total_liability = selected_client_summary['Balance Plus Accruals'].apply(lambda x: float(x.replace('$', '').replace(',', ''))).sum()
        st.write(f"Total Tax Liability for selected client: ${total_liability:.2f}")

        # Export option
        csv = selected_client_summary.to_csv(index=False)
        st.download_button(
            label="Download Selected Client Summary as CSV",
            data=csv,
            file_name=f"client_summary_{selected_ssn_last_four}.csv",
            mime="text/csv",
        )

        # Detailed Document View
        st.header("Detailed Document View", divider='blue')
        st.write("Expand the sections below to view details of individual documents.")

        for i, (result, uploaded_file) in enumerate(zip(results, uploaded_files)):
            with st.expander(f"Document {i+1}: {uploaded_file.name}"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write(f"Transcript Type: {result['Transcript Type']}")
                    st.write(f"Tracking Number: {result['Tracking Number']}")
                    st.write(f"Tax Period: {result['Tax Period']}")
                    st.write(f"SSN: {result['SSN']}")
                    
                    st.write("Income and Details:")
                    if result['Transcript Type'] in ["Account Transcript", "Record of Account", "Wage and Income Summary"]:
                        df = pd.DataFrame.from_dict(result['Income'], orient='index', columns=['Value'])
                        df.index.name = 'Field'
                        st.dataframe(df)
                    else:
                        for form, income_data in result['Income'].items():
                            st.write(f"  {form}:")
                            flat_data = flatten_dict(income_data)
                            df = pd.DataFrame.from_dict(flat_data, orient='index', columns=['Value'])
                            df.index.name = 'Field'
                            st.dataframe(df)
                
                with col2:
                    st.write("Original Document:")
                    if uploaded_file.type == "application/pdf":
                        display_pdf(uploaded_file)
                    else:
                        st.text(uploaded_file.getvalue().decode("utf-8"))

if __name__ == "__main__":
    main()