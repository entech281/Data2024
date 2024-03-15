import streamlit as st


col1,col2,col3,col4=st.columns([.1,.1,.1,.1])

with col1:
    st.page_link("Scouting.py", label="Home")
with col2:
    st.page_link("pages/1_PitScouting.py", label="PitScouting")
with col3:
    st.page_link("pages/2_MatchScouting.py", label="MatchScouting")
with col4:
    st.page_link("pages/3_Data.py", label="Analyze Data")

