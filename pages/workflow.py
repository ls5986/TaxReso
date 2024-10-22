import streamlit as st

# Function to display the overall workflow
def show_overall_workflow():
    st.title("Overall Tax Resolution Workflow")
    
    # Display a simple markdown-based workflow
    st.markdown("""
    ### Tax Resolution Workflow
    1. **Lead and Opportunity (Sales)**: Client agrees to the $795 TI and signs 8821.
    2. **Transcript Data Extraction**: Extract data from IRS transcripts.
    3. **Service Recommendations**: Recommend services based on the extracted data.
    4. **Onboarding**: Client uploads required documents.
    5. **Tax Preparation**: Prepare tax returns for unfiled years or amendments.
    6. **Resolution**: Submit Offer in Compromise or other resolution documents to the IRS.
    7. **Case Closure**: Track and close the case once the IRS approves the resolution.
    """)
    
    st.subheader("Select a step to drill down into details:")
    
    # Dropdown to select which stage to drill down into
    stages = ['Lead and Opportunity (Sales)', 'Transcript Data Extraction', 'Service Recommendations',
              'Onboarding', 'Tax Preparation', 'Resolution', 'Case Closure']
    stage = st.selectbox("Select a workflow stage", stages)
    
    return stage

# Functions to display details for each workflow step
def show_sales_details():
    st.title("Lead and Opportunity (Sales)")
    st.markdown("""
    - **Action**: Sell the Tax Investigation (TI) for $795 and get the client to sign the 8821 form.
    - **Next Steps**: Once the payment and form are received, proceed to Transcript Data Extraction.
    """)

def show_transcript_extraction_details():
    st.title("Transcript Data Extraction")
    st.markdown("""
    - **Action**: Extract data from IRS transcripts, including:
      - Self-Employment Income (SE)
      - Non-SE Income
      - Tax Withholdings
      - Levies, Garnishments, and Legal Actions
    - **Next Steps**: Use this data to recommend services.
    """)

def show_service_recommendations_details():
    st.title("Service Recommendations")
    st.markdown("""
    - **Action**: Based on transcript data, recommend services such as:
      - Filing for unfiled years
      - Amendments for underreported income
      - Offer in Compromise (OIC)
      - Currently Not Collectible (CNC)
    - **Next Steps**: If the client agrees, move to Onboarding.
    """)

def show_onboarding_details():
    st.title("Onboarding")
    st.markdown("""
    - **Action**: Verify that the client has uploaded all required documents, such as:
      - Proof of identity
      - IRS transcripts
      - W-2s, 1099s, and other financial documents
    - **Next Steps**: Proceed to Tax Preparation or Resolution depending on the client’s needs.
    """)

def show_tax_prep_details():
    st.title("Tax Preparation")
    st.markdown("""
    - **Action**: Prepare tax returns for unfiled years, or file amendments for discrepancies in prior years.
    - **Next Steps**: Once tax returns are complete, move to Resolution.
    """)

def show_resolution_details():
    st.title("Resolution")
    st.markdown("""
    - **Action**: Submit resolution documents to the IRS, such as:
      - Offer in Compromise (OIC)
      - Currently Not Collectible (CNC)
    - **Next Steps**: Monitor the IRS response and ensure all necessary documents are provided.
    """)

def show_case_closure_details():
    st.title("Case Closure")
    st.markdown("""
    - **Action**: Once the IRS accepts the resolution, close the case.
    - **Next Steps**: Confirm with the client that their case is resolved and provide any additional documentation.
    """)

# Main app logic
def main():
    # Show the overall workflow and let the user select a stage
    selected_stage = show_overall_workflow()
    
    # Drill down into the selected stage
    if selected_stage == 'Lead and Opportunity (Sales)':
        show_sales_details()
    elif selected_stage == 'Transcript Data Extraction':
        show_transcript_extraction_details()
    elif selected_stage == 'Service Recommendations':
        show_service_recommendations_details()
    elif selected_stage == 'Onboarding':
        show_onboarding_details()
    elif selected_stage == 'Tax Preparation':
        show_tax_prep_details()
    elif selected_stage == 'Resolution':
        show_resolution_details()
    elif selected_stage == 'Case Closure':
        show_case_closure_details()

if __name__ == "__main__":
    main()

