import streamlit as st
import pandas as pd
import requests
from utils.transcript_parser import parse_transcript, flatten_dict
from utils.pdf_utils import extract_text_from_pdf, display_pdf, process_transcripts
from utils.tax_utils import get_irs_standards, calculate_tax, create_tax_projection
from utils.client_sum import create_client_summary


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def extract_float(value: str) -> float:
    try:
        return float(value.replace(',', '').replace('$', ''))
    except ValueError:
        return 0.0



def get_last_four_ssn(ssn: str) -> str:
    return ssn[-4:] if len(ssn) >= 4 else "Unknown"



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
