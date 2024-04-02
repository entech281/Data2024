import config
import streamlit as st
config.configure(st.secrets) #TODO: how to ensure this happens no matter which page you start on?
import controller


pit_data = controller.load_pit_data()
st.title("Pit Data")

if len(pit_data) == 0:
    st.header("No Data")
    st.stop()

st.header("Pit Data")
st.dataframe(data=pit_data, height=600, column_config={
    # a stacked bar here woudl be ideal!
    # these oculd also be over time which would be cool too
    "tstamp": st.column_config.DatetimeColumn(),
    "robot_pickup": st.column_config.ListColumn(
        "RobotPickup"
    ),
    "pref_shoot": st.column_config.ListColumn(
        "Shooting Prefs"
    ),
    "autos": st.column_config.ListColumn(
        "Autos"
    ),
})