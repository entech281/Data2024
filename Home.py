import streamlit as st
import tba

#TODO: how to do these once across all modules
TBA_EVENT_KEY = '2024sccha'
SECRETS = st.secrets["gsheets"]
tba.set_auth_key(st.secrets["tba"]["auth_key"])

st.set_page_config(layout="wide")

st.title("281 2024 DCMP Scouting")






