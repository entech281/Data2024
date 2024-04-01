import streamlit as st
import team_analysis
import tba
import gsheet_backend
import plotly.express as px

CACHE_SECONDS = 60
SECRETS = st.secrets["gsheets"]


st.title("Defense Analysis")
@st.cache_data(ttl=CACHE_SECONDS)
def load_match_data():
    raw_data = gsheet_backend.get_match_data(SECRETS)
    return team_analysis.analyze(raw_data)




tba.set_auth_key(st.secrets["tba"]["auth_key"])
teamlist = tba.get_all_pch_team_numbers()
(analyzed, summary) = load_match_data()
focus_team = st.selectbox("Look at  Team", options=teamlist, key="defense_team")

if len(analyzed) == 0:
    st.header("No Data")
    st.stop()

if focus_team:
    st.header("Team Details for %s" % focus_team)
    general_comments = team_analysis.get_comments_for_team(focus_team, analyzed, 'notes')
    perf_over_time = analyzed[analyzed['team.number'] == focus_team]

    if len(perf_over_time == 0):
        st.write("No Peformance Data")
        st.stop()

    s = summary[summary['team.number'] == focus_team].to_dict(orient='records')
    if len(s) > 0:
        s = s[0]
        summary_row = {
            'avg_speed': "{:.2f}".format(s['avg_speed'])
        }
    else:
        st.write("No Summary Data")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Avg Speed", value=summary_row['avg_speed'])
    with col2:
        pass
    st.header("defense rating timeline")
    plot3 = px.bar(perf_over_time, x='match.number', y='defense.rating')
    plot3.update_layout(height=300)
    st.plotly_chart(plot3)

    st.header("fouls vs fouls caused")
    plot3 = px.bar(perf_over_time, x='fouls', y='defense.forced.penalties')
    plot3.update_layout(height=300)
    st.plotly_chart(plot3)

    st.header("General Notes")
    st.dataframe(general_comments)