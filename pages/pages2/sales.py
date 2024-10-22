import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
from utils.data_loader import load_data

# Load data from the JSON file
data = load_data()

# Sales Rep Dashboard logic
def sales_rep_dashboard():
    st.title("Sales Rep Dashboard")
    st.subheader("Lead Generation & TI Sale Flow")

    # Check if 'tasks' key exists in 'sales_rep'
    if "tasks" in data["sales_rep"]:
        sales_rep_tasks = pd.DataFrame(data['sales_rep']['tasks'])
        sales_rep_leads = pd.DataFrame(data['sales_rep']['leads'])

        # Set up grid options to allow row selection
        gb = GridOptionsBuilder.from_dataframe(sales_rep_tasks)
        gb.configure_selection('single', use_checkbox=True)
        grid_options = gb.build()

        # Display the interactive grid for tasks
        st.subheader("Sales Rep Tasks")
        grid_response = AgGrid(
            sales_rep_tasks,
            gridOptions=grid_options,
            height=300,
            fit_columns_on_grid_load=True,
            update_mode='SELECTION_CHANGED'
        )

        # Show details of the selected task
        selected = grid_response['selected_rows']
        if selected:
            st.write(f"Selected Task: {selected[0]['client']} - Status: {selected[0]['status']}")
            if st.button("Simulate Lead Conversion"):
                st.success(f"Lead {selected[0]['client']} converted to Client!")

        # Visualize Lead Status Breakdown using Plotly
        st.subheader("Lead Status Breakdown")
        lead_status_data = sales_rep_leads['status'].value_counts().reset_index()
        lead_status_data.columns = ['Lead Status', 'Count']

        # Create Plotly bar chart
        fig = px.bar(lead_status_data, x='Lead Status', y='Count', title="Lead Status Breakdown")
        st.plotly_chart(fig)
    else:
        st.error("No tasks found for the Sales Rep.")

sales_rep_dashboard()
