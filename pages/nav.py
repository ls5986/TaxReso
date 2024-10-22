import streamlit as st

# Main navigation
def main():
    st.sidebar.title("Navigation")
    section = st.sidebar.radio("Go to", ("Overview", "Key Stages", "Roles & Permissions", "Workflows & Logic", "UI & UX Requirements"))

    # Render each section based on user choice
    if section == "Overview":
        show_overview()
    elif section == "Key Stages":
        show_key_stages()
    elif section == "Roles & Permissions":
        show_roles_permissions()
    elif section == "Workflows & Logic":
        show_workflows_logic()
    elif section == "UI & UX Requirements":
        show_ui_ux()

# Section 1: Overview


def show_overview():
    st.title("Overview of the Tax Resolution Process")

    # Project Goal and Purpose
    st.subheader("Project Goal & Purpose")
    st.markdown("""
    The purpose of this app is to provide a comprehensive platform for managing tax resolution cases, from the initial lead generation through to case closure. 
    The system is designed to streamline the workflow for sales, tax investigation, onboarding, tax preparation, and resolution departments.
    
    **Goal**: Ensure the efficient, user-friendly handling of tax resolution cases while providing clear workflows, roles, and automated processes for each stage.
    """)

    # High-Level Workflow with Interactive Graph
    st.subheader("Interactive Workflow of the Tax Resolution Process")
    st.markdown("""
    This workflow shows the main stages of the tax resolution process. Each colored box represents a key stage, and the arrows represent the flow from one stage to another.
    """)

    # Graphviz for colored interactive workflow
    st.graphviz_chart("""
    digraph G {
        node [style=filled, color=lightblue, shape=box, fontname=Arial];
        Lead_Opportunity [label="1. Lead and Opportunity", color="#1f77b4"];
        Transcript_Extraction [label="2. Transcript Data Extraction", color="#ff7f0e"];
        Service_Recommendations [label="3. Service Recommendations", color="#2ca02c"];
        Onboarding [label="4. Onboarding", color="#d62728"];
        Tax_Preparation [label="5. Tax Preparation", color="#9467bd"];
        Resolution [label="6. Resolution", color="#8c564b"];
        Case_Closure [label="7. Case Closure", color="#e377c2"];

        Lead_Opportunity -> Transcript_Extraction [label="Sell TI & get 8821 signed"];
        Transcript_Extraction -> Service_Recommendations [label="Extract data from transcripts"];
        Service_Recommendations -> Onboarding [label="Propose services & pricing"];
        Onboarding -> Tax_Preparation [label="Verify documents"];
        Tax_Preparation -> Resolution [label="Prepare returns/amendments"];
        Resolution -> Case_Closure [label="Submit to IRS, close case"];
    }
    """)

    # Target Audience
    st.subheader("Target Audience")
    st.markdown("""
    This documentation is intended for:
    - **Developers**: To understand the logic and workflows required to implement the system.
    - **UI/UX Designers**: To design user-friendly interfaces for different departments and stages.
    - **System Architects**: To grasp the structure, flow, and dependencies of the system.
    """)

    # Main Stages of the Process (brief descriptions)
    st.subheader("Main Stages of the Process")
    st.markdown("""
    Below are the primary stages involved in the tax resolution workflow. You can find more detailed information in the respective sections of this app.

    - **Lead and Opportunity**: The sales team sells the Tax Investigation (TI) for $795 and collects 8821 forms from clients.
    - **Transcript Data Extraction**: Extract critical financial data from IRS transcripts, including SE/Non-SE income, withholdings, and legal actions.
    - **Service Recommendations**: Recommend specific services like filing for unfiled years, amendments, or proposing resolutions based on IRS data.
    - **Onboarding**: Collect and verify the client’s documents before moving to tax preparation or resolution.
    - **Tax Preparation**: Prepare and file tax returns for unfiled years or file amendments for prior discrepancies.
    - **Resolution**: Submit Offer in Compromise (OIC) or Currently Not Collectible (CNC) requests to the IRS based on the client’s situation.
    - **Case Closure**: Once the IRS accepts the proposed resolution, the case is closed, and the client is notified.

    Navigate through the sidebar to explore each stage in more detail.
    """)

    # Next Steps
    st.subheader("Next Steps")
    st.markdown("""
    Use the navigation sidebar to explore detailed sections on:
    - **Key Stages**: Dive deeper into each stage of the process with specific actions, logic, and workflows.
    - **Roles & Permissions**: Understand the roles of different departments and team members in the process.
    - **Workflows & Logic**: Get into the specifics of how each stage operates and the underlying logic for decisions.
    - **UI/UX Requirements**: See what’s needed for designing an intuitive and user-friendly system.
    """)



# Section 2: Key Stages of the Workflow (with logic and workflows)
def show_key_stages():
    st.title("Key Stages of the Workflow")
    
    # Stage 1: Lead and Opportunity (Sales)
    st.subheader("1. Lead and Opportunity (Sales)")
    st.markdown("""
    - **Goal**: Sell the Tax Investigation (TI) for $795 and obtain signed 8821 forms.
    - **Actions**: 
      - Client agrees to the TI fee.
      - Obtain signed 8821 forms for both the client and their spouse.
      - Once these are completed, move to Transcript Data Extraction.
    """)

    # Workflow for Lead and Opportunity
    st.graphviz_chart("""
        digraph {
            Lead_Opportunity -> Sell_TI [label="Sell $795 TI"]
            Sell_TI -> Sign_8821 [label="Client signs 8821 form"]
            Sign_8821 -> Transcript_Extraction [label="Move to Transcript Data Extraction"]
        }
    """)

    # Stage 2: Transcript Data Extraction
    st.subheader("2. Transcript Data Extraction")
    st.markdown("""
    - **Goal**: Extract critical financial data from IRS transcripts.
    - **Actions**: 
      - Extract SE and Non-SE income, tax withholdings, legal actions (e.g., garnishments, levies).
      - Identify any IRS legal actions (e.g., garnishments) that need to be immediately addressed.
    """)

    st.graphviz_chart("""
        digraph {
            Transcript_Extraction -> Extract_SE [label="Extract SE Income"]
            Transcript_Extraction -> Extract_NonSE [label="Extract Non-SE Income"]
            Transcript_Extraction -> Extract_Withholdings [label="Extract Tax Withholdings"]
            Transcript_Extraction -> Scan_Legal [label="Scan for Levies/Garnishments"]
            Scan_Legal -> Immediate_Resolution [label="If garnishments, move to Resolution"]
        }
    """)

    st.markdown("""
    **Transcript Data Extraction Logic**:
    - **Self-Employment Income (SE)**: Forms like 1099-MISC, 1099-NEC, and other SE income forms are used to calculate SE income.
    - **Non-SE Income**: Forms like W-2, 1099-INT, 1099-DIV are used to capture non-SE income and withholdings.
    - **Withholdings**: Calculate the total withholdings based on the client’s tax forms.
    - **Scan for Legal Actions**: Identify IRS actions like garnishments, levies, and liens. If found, the case moves directly to resolution.
    """)

    # Stage 3: Service Recommendations
    st.subheader("3. Service Recommendations")
    st.markdown("""
    - **Goal**: Recommend appropriate services based on the transcript data.
    - **Actions**:
      - Recommend services such as filing for unfiled years, amending prior-year returns, or proposing Offer in Compromise (OIC) or Currently Not Collectible (CNC).
      - Prepare the pricing based on the service recommendations.
      - Get client approval to proceed to onboarding.
    """)

    st.graphviz_chart("""
        digraph {
            Transcript_Extraction -> Recommend_Services [label="Analyze Extracted Data"]
            Recommend_Services -> Filing_Years [label="Recommend Filing for Unfiled Tax Years"]
            Recommend_Services -> Amendments [label="Recommend Amendments"]
            Recommend_Services -> OIC [label="Offer in Compromise"]
            Recommend_Services -> CNC [label="Currently Not Collectible"]
        }
    """)

    st.markdown("""
    **Service Recommendation Logic**:
    - **Filing for Unfiled Years**: Recommend filing if IRS transcripts show missing tax years.
    - **Amendments**: Recommend amendments if the IRS income records don't match filed returns.
    - **Offer in Compromise (OIC)**: Propose an OIC if the client qualifies based on their financial situation.
    - **Currently Not Collectible (CNC)**: Recommend CNC if the client has no ability to pay, based on IRS standards.
    """)

    # Stage 4: Onboarding
    st.subheader("4. Onboarding")
    st.markdown("""
    - **Goal**: Collect all required client documents before proceeding to tax preparation or resolution.
    - **Actions**: 
      - Request documents from the client (e.g., proof of identity, W-2s, 1099s, financial statements).
      - Verify that all required documents are uploaded.
    """)

    st.graphviz_chart("""
        digraph {
            Recommend_Services -> Request_Docs [label="Request Client Documents"]
            Request_Docs -> Verify_Docs [label="Verify Document Uploads"]
            Verify_Docs -> Tax_Prep [label="Move to Tax Prep if complete"]
            Verify_Docs -> Resolution [label="Move to Resolution if incomplete or garnishment found"]
        }
    """)

    st.markdown("""
    **Onboarding Document Logic**:
    - Request specific documents based on the service recommendations.
    - If the client has unfiled tax years, request W-2s, 1099s, and profit & loss statements (if self-employed).
    - If IRS legal actions are identified, move directly to resolution.
    """)

    # Stage 5: Tax Preparation
    st.subheader("5. Tax Preparation")
    st.markdown("""
    - **Goal**: Prepare tax returns for unfiled years or amend prior returns based on the extracted data.
    - **Actions**: 
      - Prepare returns for missing tax years.
      - File amendments for discrepancies found in previous returns (based on IRS transcripts).
    """)

    st.graphviz_chart("""
        digraph {
            Verify_Docs -> Tax_Return_Prep [label="Prepare Tax Returns for Unfiled Years"]
            Verify_Docs -> Amend_Returns [label="File Amendments for Prior Years"]
            Tax_Return_Prep -> Submit_Returns [label="Submit Returns to IRS"]
        }
    """)

    # Stage 6: Resolution
    st.subheader("6. Resolution")
    st.markdown("""
    - **Goal**: Submit Offer in Compromise (OIC) or Currently Not Collectible (CNC) requests to the IRS based on the client's situation.
    - **Actions**:
      - Prepare and submit OIC or CNC requests.
      - Track the IRS response and provide additional documentation if requested.
    """)

    st.graphviz_chart("""
        digraph {
            Tax_Return_Prep -> Prepare_OIC [label="Prepare Offer in Compromise"]
            Amend_Returns -> Prepare_CNC [label="Prepare Currently Not Collectible"]
            Prepare_OIC -> IRS_Response [label="Submit OIC"]
            Prepare_CNC -> IRS_Response [label="Submit CNC"]
        }
    """)

    st.markdown("""
    **Resolution Logic**:
    - **Offer in Compromise (OIC)**: If the client qualifies based on income, expenses, and ability to pay, submit an OIC.
    - **Currently Not Collectible (CNC)**: If the client has no disposable income, file for CNC status.
    - **IRS Response**: Track the IRS response and provide additional documentation if required.
    """)

    # Stage 7: Case Closure
    st.subheader("7. Case Closure")
    st.markdown("""
    - **Goal**: Close the case after the IRS accepts the proposed resolution.
    - **Actions**:
      - Confirm IRS acceptance of the resolution (OIC/CNC).
      - Provide final resolution documents to the client and close the case.
    """)

    st.graphviz_chart("""
        digraph {
            IRS_Response -> Close_Case [label="If IRS accepts, close the case"]
            Close_Case -> Provide_Final_Docs [label="Provide Final Docs to Client"]
        }
    """)

# Section 3: Roles & Permissions
def show_roles_permissions():
    st.title("Roles & Permissions")

    st.subheader("Sales Department")
    st.markdown("""
    - **Sales Executive**: High-level view of leads, conversions, and performance.
    - **Sales Manager**: View of team members’ individual performance and the ability to assign or reassign leads.
    - **Sales Representative**: Dashboard showing open leads, callbacks, and TI sales.
    """)

    st.subheader("Tax Investigation (TI) Department")
    st.markdown("""
    - **TI Executive**: Overview of all tax investigations and their current status.
    - **TI I (Junior)**: Assigned to review IRS transcripts for basic data extraction.
    - **TI II (Intermediate)**: Handles more detailed investigations and validation.
    - **TI III (Senior)**: Reviews complex cases and prepares final reports for resolution.
    """)

    # Add other roles and permissions...

# Section 4: Workflows & Logic (full logic for data extraction, document requests, etc.)
def show_workflows_logic():
    st.title("Workflows & Logic")

    st.subheader("Transcript Data Extraction Logic")
    st.markdown("""
    - Extract SE (Self-Employment) income, Non-SE income, tax withholdings, garnishments, levies, and other legal actions.
    - Identify any urgent legal actions like garnishments, which will direct the case straight to resolution.
    """)

    st.subheader("Document Requirements Based on Income Types")
    st.markdown("""
    - **W-2 Income**: Requires W-2 form.
    - **1099 Income**: Requires 1099 form (e.g., 1099-MISC, 1099-NEC, etc.).
    - **Self-Employment**: Requires Profit & Loss (P&L) statements and other related documents.
    """)

    # Add more workflow and logic details...

# Section 5: UI & UX Requirements
def show_ui_ux():
    st.title("UI & UX Requirements")

    st.subheader("Main Workflow Visualization")
    st.markdown("""
    - A visual representation of the overall workflow, with each stage clearly labeled.
    - Users should be able to click on each stage to drill down into the details of that step.
    """)

    st.subheader("Role-Based Dashboards")
    st.markdown("""
    - Each department should have a customized dashboard showing tasks, leads, cases, or documents relevant to their role.
    """)

    # Add more UI/UX details...

# Run the app
if __name__ == "__main__":
    main()
