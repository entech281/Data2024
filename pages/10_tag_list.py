import config
import streamlit as st
config.configure(st.secrets) #TODO: how to ensure this happens no matter which page you start on?
import gsheet_backend
import controller

tag_manager = gsheet_backend.get_tag_manager()


st.set_page_config(layout="wide")
st.title("Tag List")
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