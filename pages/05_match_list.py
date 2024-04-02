import config
import streamlit as st
config.configure(st.secrets) #TODO: how to ensure this happens no matter which page you start on?
import gsheet_backend
import controller
import team_analysis
import tba

st.set_page_config(layout="wide")
st.title("Analyzed Match Data")

tag_manager = gsheet_backend.get_tag_manager()
(analyzed, summary) = controller.load_match_data()
teamlist = tba.get_all_pch_team_numbers()


if len(analyzed) == 0:
    st.header("No Data")
    st.stop()


st.text("Choose Filters")
col1, col2, col3 = st.columns(3)
filtered_data = analyzed
filtered_summary = summary
with col1:
    pickup_filter = st.multiselect("Ground Pickup", options=list(analyzed['robot.pickup'].unique()))
    if len(pickup_filter) > 0:
        filtered_data = filtered_data[filtered_data['robot.pickup'].isin(pickup_filter)]

with col2:
    climbed = st.checkbox("Climbed?")
    if climbed:
        filtered_data = filtered_data[filtered_data["climb"] == "Yes"]

    MIN_FOULS = 0
    MAX_FOULS = max(analyzed["fouls"].max(), 1)
    fouls = st.slider("Fouls", MIN_FOULS, MAX_FOULS, (MIN_FOULS, MAX_FOULS))
    (min_selected_fouls, max_selected_fouls) = fouls
    filtered_data = filtered_data[filtered_data["fouls"] >= min_selected_fouls]
    filtered_data = filtered_data[filtered_data["fouls"] <= max_selected_fouls]

with col3:
    match_type_filter = st.selectbox("Match Type", options=['Any', 'Qualifier', 'Final'])
    if match_type_filter:
        if match_type_filter == "Qualifier":
            filtered_data = filtered_data[filtered_data["match.number"].str.startswith('Q')]
        elif match_type_filter == 'Final':
            filtered_data = filtered_data[filtered_data["match.number"].str.startswith('F')]

st.header("{d} Matches".format(d=len(filtered_data)))

# see optoins here: https://docs.streamlit.io/library/api-reference/data/st.dataframe
filtered_data_with_summary = team_analysis.compute_bar_scoring_summaries(filtered_data)
st.dataframe(filtered_data_with_summary, use_container_width=True, hide_index=True, column_config={
    # a stacked bar here woudl be ideal!
    # these oculd also be over time which would be cool too
    "total_amp_notes": st.column_config.ProgressColumn(
        "Amp Notes Total",
        help="Auto+Tele",
        format="%f",
        min_value=0,
        max_value=30,
    ),
    "total_spk_notes": st.column_config.ProgressColumn(
        "Teleop Notes Total",
        help="Auto+Tele",
        format="%f",
        min_value=0,
        max_value=30,
    ),
    'auto_scoring_summary': st.column_config.BarChartColumn(
        "Auto: AMP SPK POD OTHER",
        y_min=0,
        y_max=5
    ),
    'teleop_scoring_summary': st.column_config.BarChartColumn(
        "Tele: AMP SPK POD OTHER",
        y_min=0,
        y_max=5
    ),

})
st.header("Team Stats")

col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

def filter_data_with_field_slider(field_name, label, df):
    calc_min = summary[field_name].min()
    calc_max = summary[field_name].max()
    s = st.slider(label, calc_min, calc_max, (calc_min, calc_max), key="slider_" + field_name)
    df = df[df[field_name] >= s[0]]
    df = df[df[field_name] <= s[1]]
    return df

with col1:
    filtered_summary = filter_data_with_field_slider("max_teleop", "Max Teleop", filtered_summary)
    filtered_summary = filter_data_with_field_slider("avg_teleop", "Avg Teleop", filtered_summary)
    filtered_summary = filter_data_with_field_slider("max_auto", "Max Auto", filtered_summary)
with col2:
    filtered_summary = filter_data_with_field_slider("avg_auto", "Avg TAuto", filtered_summary)
    filtered_summary = filter_data_with_field_slider("max_total_pts", "Total,Max", filtered_summary)
    filtered_summary = filter_data_with_field_slider("avg_total_pts", "Total,Avg", filtered_summary)

with col3:
    filtered_summary = filter_data_with_field_slider("avg_notes_speaker", "Speaker,Avg", filtered_summary)
    filtered_summary = filter_data_with_field_slider("avg_notes_amp", "Amp,Avg", filtered_summary)

with col4:
    pass

with col5:
    pass

with col6:
    pass

with col7:
    pass

with col8:
    pass

st.header("{d} Matching teams".format(d=len(filtered_summary)))
st.dataframe(data=filtered_summary)