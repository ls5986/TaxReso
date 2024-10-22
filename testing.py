import streamlit as st
from utils.client_sum import create_client_summary
from utils.pdf_utils import display_pdf
from utils.form_calculations import calculate_based_on_form

# Rest of your code...

for i, (result, uploaded_file) in enumerate(zip(selected_client_results, selected_client_files)):
    with st.expander(f"Document {i+1}: {uploaded_file.name}"):
        col1, col2 = st.columns([1, 1])

        with col1:
            st.write(f"Transcript Type: {result['Transcript Type']}")
            st.write(f"Tracking Number: {result['Tracking Number']}")
            st.write(f"Tax Period: {result['Tax Period']}")
            st.write(f"SSN: {result['SSN']}")

            # Extract the form type and pass to the appropriate calculation logic
            form_type = result['Transcript Type']
            calculation_result = calculate_based_on_form(form_type, result)
            st.write("Calculation Result:", calculation_result["calculation"])

            st.write("Income and Details:")
            # Display relevant data in a tabular format, based on form type or result

        with col2:
            st.write("Original Document:")
            if uploaded_file.type == "application/pdf":
                display_pdf(uploaded_file)
            else:
                st.text(uploaded_file.getvalue().decode("utf-8"))////



                import streamlit as st
import pandas as pd
from utils.client_sum import create_client_summary
from utils.pdf_utils import display_pdf
from utils.form_extraction import extract_income_withholdings
from utils.common import extract_float, get_last_four_ssn

# Set page configuration for wider screen layout
st.set_page_config(layout="wide")

st.title("Client Summary")

if 'results' in st.session_state:
    results = st.session_state['results']
    client_summary = create_client_summary(results)

    unique_ssn_last_four = client_summary['SSN Last Four'].unique()
    selected_ssn_last_four = st.selectbox("Select a client (Last 4 digits of SSN):", unique_ssn_last_four)

    selected_client_summary = client_summary[client_summary['SSN Last Four'] == selected_ssn_last_four]

    # Highlight unfiled returns
    styled_df = selected_client_summary.style.apply(lambda row: ['background-color: red' if row['Return Filed'] == 'No' else '' for _ in row], axis=1)
    st.dataframe(styled_df, use_container_width=True)

    # Calculate total tax liability for all years using 'Current Balance'
    total_balance = selected_client_summary['Balance Plus Accruals']
    total_balance_sum = total_balance.apply(lambda x: float(x.replace('$', '').replace(',', ''))).sum()

    # Calculate total projected amount owed for unfiled returns
    total_projected = selected_client_summary[selected_client_summary['Return Filed'] == 'No']['Projected Amount Owed']
    total_projected_sum = total_projected.apply(lambda x: float(x.replace('$', '').replace(',', ''))).sum()

    # Display the calculated totals
    st.write(f"Total Tax Liability for selected client: ${total_balance_sum:.2f}")
    st.write(f"Total Projected Amount Owed for Unfiled Returns: ${total_projected_sum:.2f}")

    # Download button for CSV of selected client summary
    csv = selected_client_summary.to_csv(index=False)
    st.download_button(
        label="Download Selected Client Summary as CSV",
        data=csv,
        file_name=f"client_summary_{selected_ssn_last_four}.csv",
        mime="text/csv",
    )

    # Display detailed information alongside PDF viewer
    st.header("Detailed Document View")
    
    # Filter results and uploaded files based on the selected client
    selected_client_results = [result for result in results if get_last_four_ssn(result['SSN']) == selected_ssn_last_four]
    selected_client_files = [file for file, result in zip(st.session_state['uploaded_files'], results) if get_last_four_ssn(result['SSN']) == selected_ssn_last_four]

    for i, (result, uploaded_file) in enumerate(zip(selected_client_results, selected_client_files)):
        col1, col2 = st.columns([1, 1])

        with col1:
            st.write(f"Transcript Type: {result['Transcript Type']}")
            st.write(f"Tracking Number: {result['Tracking Number']}")
            st.write(f"Tax Period: {result['Tax Period']}")
            st.write(f"SSN: {result['SSN']}")

            # Extract and display relevant income and withholding data
            form_type = result['Transcript Type']
            extracted_data = extract_income_withholdings(form_type, result['Income'])
            if extracted_data['Income'] or extracted_data['Withholdings']:
                st.write("Income Details:")
                st.table(pd.DataFrame.from_dict(extracted_data['Income'], orient='index', columns=['Value']))
                st.write("Withholdings:")
                st.table(pd.DataFrame.from_dict(extracted_data['Withholdings'], orient='index', columns=['Value']))

        with col2:
            st.write("Original Document:")
            if uploaded_file.type == "application/pdf":
                display_pdf(uploaded_file)
            else:
                st.text(uploaded_file.getvalue().decode("utf-8"))
else:
    st.warning("Please upload and process transcripts first.")
