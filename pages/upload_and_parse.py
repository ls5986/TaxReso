import streamlit as st
import pandas as pd
from utils.transcript_parser import parse_transcript
from utils.pdf_utils import extract_text_from_pdf, display_pdf
from utils.client_sum import create_client_summary
from utils.common import get_last_four_ssn

def highlight_not_filed(row):
    color = 'red' if row['Return Filed'] == 'No' else ''
    return ['background-color: {}'.format(color) for _ in row]

# Set page configuration for wider screen layout
st.set_page_config(layout="wide")

# Check if results already exist to control expander
show_file_uploader = not ('results' in st.session_state and 'uploaded_files' in st.session_state)

# File Upload section inside an expander that collapses after upload
with st.expander("Upload and Process Tax Transcript Files", expanded=show_file_uploader):
    uploaded_files = st.file_uploader("Choose tax transcript files", accept_multiple_files=True, type=['pdf', 'txt'])

# Process and store the uploaded files
if uploaded_files:
    all_transcripts = []
    results = []

    # Extract text and save both results and original uploaded files
    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            text_content = extract_text_from_pdf(uploaded_file)
        else:
            text_content = uploaded_file.getvalue().decode("utf-8")

        all_transcripts.append(text_content)
        results.append(parse_transcript(text_content))

    # Save the results and uploaded files into session state
    st.session_state['results'] = results
    st.session_state['uploaded_files'] = uploaded_files

    st.success("Transcripts processed successfully! You can now view the client summary below.")

# Show client summary and original document viewer if transcripts are processed
if 'results' in st.session_state and 'uploaded_files' in st.session_state:
    st.subheader("Client Summary")

    results = st.session_state['results']
    uploaded_files = st.session_state['uploaded_files']

    # Create client summary from results
    client_summary = create_client_summary(results)

    # Get unique SSN last four digits for client selection
    unique_ssn_last_four = client_summary['SSN Last Four'].unique()
    selected_ssn_last_four = st.selectbox("Select a client (Last 4 digits of SSN):", unique_ssn_last_four)

    # Filter summary for selected client
    selected_client_summary = client_summary[client_summary['SSN Last Four'] == selected_ssn_last_four]

    # Highlight unfiled returns
    styled_df = selected_client_summary.style.apply(highlight_not_filed, axis=1)
    st.dataframe(styled_df, use_container_width=True)

    # Calculate total tax liability using 'Current Balance'
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

    # Display original documents for selected client alongside relevant data in table format
    st.header("Original Document Viewer & Relevant Data Analysis")
    selected_client_files = [
        file for file, result in zip(uploaded_files, results)
        if get_last_four_ssn(result['SSN']) == selected_ssn_last_four
    ]
    selected_client_results = [
        result for result in results if get_last_four_ssn(result['SSN']) == selected_ssn_last_four
    ]

    for i, (result, uploaded_file) in enumerate(zip(selected_client_results, selected_client_files)):
        with st.expander(f"Document {i + 1}: {uploaded_file.name}"):
            # Create two columns, one for the PDF and the other for the relevant data analysis
            col1, col2 = st.columns([2, 2])
            
            # Column for displaying the document
            with col1:
                st.write("Original Document:")
                if uploaded_file.type == "application/pdf":
                    display_pdf(uploaded_file)
                else:
                    st.text(uploaded_file.getvalue().decode("utf-8"))

            # Column for displaying relevant data in a table-like format
            with col2:
                st.write("Relevant Data Analysis for Selected Document")

                # Display relevant fields based on transcript type
                transcript_type = result.get('Transcript Type', 'Unknown')
                data_table = []

                if transcript_type == "Account Transcript":
                    # Show specific fields for Account Transcript
                    relevant_keys = ['Tax Period', 'Tracking Number', 'Return Filed', 'Adjusted Gross Income', 'Taxable Income']
                elif transcript_type == "Wage and Income Transcript" or transcript_type == "Wage and Income Summary":
                    # Show specific fields for Wage and Income Transcript or Summary (exclude 'Return Filed')
                    relevant_keys = ['Tax Period', 'Tracking Number', 'Income Types', 'Withholdings']
                elif transcript_type == "Record of Account":
                    # Show specific fields for Record of Account
                    relevant_keys = ['Tax Period', 'Tracking Number', 'Return Filed', 'Adjusted Gross Income', 'Tax Per Return']
                else:
                    # Default fields
                    relevant_keys = ['Tax Period', 'Tracking Number', 'SSN']

                for key in relevant_keys:
                    data_table.append((key, result.get(key, 'Not Available')))

                # Convert relevant data into DataFrame for better display in Streamlit
                relevant_data_df = pd.DataFrame(data_table, columns=["Field", "Value"])
                st.table(relevant_data_df)

                # Details Button for extra information
                if st.button(f"Show Details for Document {i + 1}"):
                    st.write("Detailed Information:")
                    details_data = []

                    # Add details if available
                    if 'Details' in result:
                        for detail in result['Details']:
                            for key, value in detail.items():
                                details_data.append((key, value))

                    # Convert detailed data into DataFrame for display
                    details_df = pd.DataFrame(details_data, columns=["Field", "Value"])
                    st.table(details_df)

else:
    st.warning("Please upload and process transcripts first.")
