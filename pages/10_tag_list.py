import streamlit as st
import gsheet_backend

SECRETS = st.secrets["gsheets"]
tag_manager = gsheet_backend.get_tag_manager(SECRETS)
st.set_page_config(layout="wide")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("tags by team")
    st.dataframe(data=tag_manager.df, hide_index=True)

with col2:
    st.subheader("Teams by Tag")
    st.dataframe(data=tag_manager.tag_summary)

with col3:
    st.subheader("defined tags")
    st.table(data=tag_manager.all_tag_list)