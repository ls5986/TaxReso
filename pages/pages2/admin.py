import streamlit as st
from utils.data_loader import load_data

data = load_data()

st.title("Admin Dashboard")
st.subheader("Manage the Entire Process")

admin_data = data["admin"]

st.write("Team Performance:")
for team_member in admin_data["team_performance"]:
    st.write(f"{team_member['name']} - Leads Converted: {team_member['leads_converted']} - Cases Open: {team_member['cases_open']}")

st.write("Case Assignments:")
for assignment in admin_data["case_assignments"]:
    st.write(f"Case {assignment['case_id']} - {assignment['client_name']} assigned to {assignment['assigned_to']}")
