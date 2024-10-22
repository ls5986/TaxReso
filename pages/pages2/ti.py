import streamlit as st
from utils.data_loader import load_data

data = load_data()

st.title("Tax Investigation Dashboard")
st.subheader("Transcript Acquisition & Initial TI Review")

case_manager_data = data["case_manager"]["clients"]

# Show client details and transcripts
for client in case_manager_data:
    st.write(f"Client: {client['name']} - TI Report: {client['TI_report']}")
    st.write("Transcripts:")
    for transcript in client["transcripts"]:
        st.write(f" - {transcript['type']}: {transcript['summary']}")
    st.write(f"Document Status: {client['document_status']}")

if st.button("Request Documents"):
    st.success("Requested documents from client.")
