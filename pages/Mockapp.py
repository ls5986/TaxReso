import streamlit as st
from utils.data_loader import load_data

# Navigation function
def navigate_to(page):
    st.session_state['page'] = page

if 'page' not in st.session_state:
    st.session_state['page'] = 'sales'  # Default to sales

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

# Load appropriate page
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
