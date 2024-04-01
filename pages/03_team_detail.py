import streamlit as st
import team_analysis
import tba
import gsheet_backend
import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap

SECRETS = st.secrets["gsheets"]

TBA_EVENT_KEY = '2024sccha'
CACHE_SECONDS = 60
tba.set_auth_key(st.secrets["tba"]["auth_key"])

def write_markdown_list(vals):
    s = ""
    for v in vals:
        s += ("* " + v + "___" + "\n")
    return s

def get_accuracy_colormap():
    c = ["darkred", "red", "lightcoral", "white", "palegreen", "green", "darkgreen"]
    v = [0, .15, .4, .5, 0.6, .9, 1.]
    l = list(zip(v, c))
    cmap = LinearSegmentedColormap.from_list('rg', l, N=256)
    return cmap

# TODO: duplicated tons
@st.cache_data(ttl=CACHE_SECONDS)
def load_match_data():
    raw_data = gsheet_backend.get_match_data(SECRETS)
    return team_analysis.analyze(raw_data)

@st.cache_data(ttl=CACHE_SECONDS)
def load_pit_data():
    raw_data = gsheet_backend.get_pits_data(SECRETS)
    return raw_data


tag_manager = gsheet_backend.get_tag_manager(SECRETS)

# TODO: duplicated in several files
def pit_data_for_team(team_num):
    all_data = load_pit_data()
    team_data = all_data[all_data['team.number'] == team_num]
    if len(team_data) > 0:
        return team_data.to_dict(orient='records')[0]
    else:
        return {}


st.title("Team Detail")

(analyzed, summary) = load_match_data()
teamlist = tba.get_all_pch_team_numbers()


# TODO: separate calculations and presentation, so that
# compare page can call it for each team, and render side-by-side
analyzed_and_filtered = analyzed
if len(analyzed_and_filtered) == 0:
    st.header("No Data")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    focus_team = st.selectbox("Choose Team", options=teamlist)
with col2:
    if focus_team:
        tm = gsheet_backend.get_tag_manager(SECRETS)
        existing_team_tags = tm.get_tags_for_team(focus_team)
        new_team_tags = st.multiselect("Team Tags", options=tm.all_tag_list, default=existing_team_tags)
        if set(new_team_tags) != set(existing_team_tags):
            tm.update_tags_for_team(focus_team, new_team_tags)
    else:
        st.subheader("<Choose Team>")
if focus_team:
    event_summary_df = team_analysis.team_summary(analyzed_and_filtered)
    analyzed_and_filtered = analyzed_and_filtered[analyzed_and_filtered["team.number"] == focus_team]
    general_comments = team_analysis.get_comments_for_team(focus_team, analyzed, 'notes')
    strategy_comments = team_analysis.get_comments_for_team(focus_team, analyzed, 'strategy')

    event_summary_df = event_summary_df[event_summary_df['team.number'] == focus_team]
    team_pit_data = pit_data_for_team(focus_team)

if len(event_summary_df) > 0:
    d = event_summary_df.to_dict(orient='records')[0]
    event_summary_dict = {
        'rank_by_avg_pts': str(d['rank_by_avg_pts']),
        'frc_rank': str(d['frc_rank']),
        'avg_total_pts': "{:.2f}".format(d['avg_total_pts']),
        'climb_pts': "{:.2f}".format(d['climb_pts']),
        'avg_notes_speaker': "{:.2f}".format(d['avg_notes_speaker']),
        'avg_notes_amp': "{:.2f}".format(d['avg_notes_amp'])
    }
else:
    event_summary_dict = {
        'rank_by_avg_pts': 'n/a',
        'frc_rank': 'n/a',
        'avg_total_pts': 'n/a',
        'climb_pts': 'n/a',
        'avg_notes_speaker': 'n/a',
        'avg_notes_amp': 'n/a'
    }
team_tba_stats = tba.get_tba_team_stats_for_team(TBA_EVENT_KEY, focus_team)
# print("Team stats=",team_tba_stats)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(label="Our Rank By Avg Pts", value=event_summary_dict['rank_by_avg_pts'])
    st.metric(label="Our Rank By Rank Pts", value=event_summary_dict['frc_rank'])
    st.metric(label="TBA Rank", value=team_tba_stats["rank"])
with col2:
    st.metric(label="Avg Match Pts", value=event_summary_dict['avg_total_pts'])
    st.metric(label="Climb Pts", value=event_summary_dict['climb_pts'])
    st.metric(label="TBA OPR", value=team_tba_stats["opr"])
with col3:
    st.metric(label="Avg Speaker Notes", value=event_summary_dict['avg_notes_speaker'])
    st.metric(label="Avg Amp Notes", value=event_summary_dict['avg_notes_amp'])
    st.metric(label="TBA DPR", value=team_tba_stats["dpr"])

with col4:
    st.caption("Robot Specs")
    if len(team_pit_data) == 0:
        st.text("[No Pit Data]")
    else:
        st.markdown(""" 
            **Dimensions** : {0:1.1f} x{1:1.1f} x {2:1.1f} h   
            **Weight**:  {3:1.1f} lb  
            **Climb** : {4:s}   
            **UnderStage** : {5:s}    
            **Drive** : {6:s}    
        """.format(
            team_pit_data["robot.width"],
            team_pit_data["robot.length"],
            team_pit_data["robot.height"],
            team_pit_data["robot.weight"],
            str(team_pit_data["climb"]),
            str(team_pit_data["under.stage"]),
            team_pit_data["robot.drive"]
        ))
        st.caption("Notes")
        st.text(team_pit_data["notes"])

with col5:
    st.caption("Scoring Characteristics")
    if len(team_pit_data) == 0:
        st.text("[No Pit Data]")
    else:
        st.markdown("""
            **Drive** : {0:s}  
            **Climb** : {1:s}  
            **Scoring Methods** : {2:s}  
            **Shooting Prefs** : {3:s}  
        """.format(
            team_pit_data["robot.drive"],
            team_pit_data["climb"],
            team_pit_data["score.abilities"],
            team_pit_data["pref.shoot"]
        ))
        st.caption("Autos")
        st.text(team_pit_data["autos"])

(auto_table, tele_table) = team_analysis.compute_scoring_table(summary, focus_team)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Auto Accuracy")
    st.dataframe(
        data=auto_table.style.background_gradient(cmap=get_accuracy_colormap(), subset='accuracy', vmin=0.0,
                                                  vmax=1.0).background_gradient(vmin=0, vmax=25,
                                                                                subset=['missed', 'made']).format(
            precision=2), hide_index=True)
with col2:
    st.subheader("Teleop Accuracy")
    st.dataframe(
        data=tele_table.style.background_gradient(cmap=get_accuracy_colormap(), subset='accuracy', vmin=0.0,
                                                  vmax=1.0).background_gradient(vmin=0, vmax=25,
                                                                                subset=['missed', 'made']).format(
            precision=2), hide_index=True)
st.header("scoring timeline")
plot3 = px.bar(analyzed_and_filtered, x='match.number',
               y=['notes.speaker.auto', 'notes.speaker.teleop', 'notes.amp.auto', 'notes.amp.teleop'])
plot3.update_layout(height=300, yaxis_title="Notes Scored")
st.plotly_chart(plot3)

st.header("General Notes")
st.markdown(write_markdown_list(general_comments))

st.header("Strategy Notes")
st.markdown(write_markdown_list(strategy_comments))
