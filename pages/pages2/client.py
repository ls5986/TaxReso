import streamlit as st
from utils.data_loader import load_data

data = load_data()

st.title("Client Dashboard")
st.subheader("Overview of Your Case")

client_data = data["client"]["clients"]

# Allow client to select their profile
client_names = [client["name"] for client in client_data]
selected_client = st.selectbox("Select your name:", client_names)

# Show client details
client = next(c for c in client_data if c["name"] == selected_client)
st.write(f"Status: {client['status']}")
st.write(f"Outstanding Documents: {', '.join(client['outstanding_docs'])}")

st.text_area("Message your Case Manager", "")
if st.button("Send Message"):
    st.success("Message sent to Case Manager.")
