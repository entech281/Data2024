import streamlit as st
import gsheet_backend

SECRETS = st.secrets["gsheets"]
CACHE_SECONDS = 60


@st.cache_data(ttl=CACHE_SECONDS)
def load_pit_data():
    raw_data = gsheet_backend.get_pits_data(SECRETS)
    return raw_data

pit_data = load_pit_data()
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