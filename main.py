import streamlit as st
from utils.data_loader import load_data  # Ensure load_data is imported from the correct location

# Set page layout
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
        .main {
            padding-left: 150px;
            padding-right: 150px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Tax Transcript Parser")

st.write("""
Welcome to the Tax Transcript Parser.
Use the sidebar to navigate through different pages for uploading, processing, and viewing client summaries.
""")

# Navigation function
def navigate_to(page):
    st.session_state['page'] = page

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'sales'  # Default to 'sales' page

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    if st.button("Sales Rep"):
        navigate_to('sales')
    if st.button("Tax Investigation"):
        navigate_to('tax_investigation')
    if st.button("Tax Prep"):
        navigate_to('tax_prep')
    if st.button("Client"):
        navigate_to('client')
    if st.button("Resolution"):
        navigate_to('resolution')
    if st.button("Admin"):
        navigate_to('admin')

# Load the appropriate page based on the session state
if st.session_state['page'] == 'sales':
    exec(open('pages/pages2/sales.py').read())
elif st.session_state['page'] == 'tax_investigation':
    exec(open('pages/pages2/ti.py').read())
elif st.session_state['page'] == 'tax_prep':
    exec(open('pages/pages2/tax_prep.py').read())
elif st.session_state['page'] == 'client':
    exec(open('pages/pages2/client.py').read())
elif st.session_state['page'] == 'resolution':
    exec(open('pages/pages2/resolution.py').read())
elif st.session_state['page'] == 'admin':
    exec(open('pages/pages2/admin.py').read())
