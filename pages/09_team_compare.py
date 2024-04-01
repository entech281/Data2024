import streamlit as st
import team_analysis
import tba
import gsheet_backend
from matplotlib.colors import LinearSegmentedColormap
st.set_page_config(layout="wide")
SECRETS = st.secrets["gsheets"]

TBA_EVENT_KEY = '2024sccha'
CACHE_SECONDS = 60
tba.set_auth_key(st.secrets["tba"]["auth_key"])
@st.cache_data(ttl=CACHE_SECONDS)
def load_match_data():
    raw_data = gsheet_backend.get_match_data(SECRETS)
    return team_analysis.analyze(raw_data)

#TODO: duplicateds with team_detail
def get_accuracy_colormap():
    c = ["darkred", "red", "lightcoral", "white", "palegreen", "green", "darkgreen"]
    v = [0, .15, .4, .5, 0.6, .9, 1.]
    l = list(zip(v, c))
    cmap = LinearSegmentedColormap.from_list('rg', l, N=256)
    return cmap

#TODO: this is garbage! and probably dont even need it now that we joined all
@st.cache_data(ttl=CACHE_SECONDS)
def load_pit_data():
    raw_data = gsheet_backend.get_pits_data(SECRETS)
    return raw_data

def pit_data_for_team(team_num):
    all_data = load_pit_data()
    team_data = all_data[all_data['team.number'] == team_num]
    if len(team_data) > 0:
        return team_data.to_dict(orient='records')[0]
    else:
        return {}

(analyzed, summary) = load_match_data()

tag_manager = gsheet_backend.get_tag_manager(SECRETS)
teamlist = tba.get_all_pch_team_numbers()
st.title("Team Compare")
teams_to_compare = st.multiselect("Select up to 3 Teams", key="compareteams", max_selections=3, options=teamlist,
                                  placeholder="")

filtered_summary = summary[summary["team.number"].isin(teams_to_compare)]



# TODO : ducpliated mostly from test foucs-- need to factor that out
def display_team(team_number, index):
    st.header(team_number)

    event_summary_df = summary[summary['team.number'] == team_number]
    team_pit_data = pit_data_for_team(team_number)
    event_summary_dict = event_summary_df.to_dict(orient='records')[0]

    avg_pts_rank = str(event_summary_dict['rank_by_avg_pts'])
    frc_rank = str(event_summary_dict['frc_rank'])

    with st.container(height=200):
        st.multiselect("Tags", key='tags' + str(index), options=tag_manager.all_tag_list,
                       default=tag_manager.get_tags_for_team(team_number))
    with st.container(height=800):

        team_tba_stats = tba.get_tba_team_stats_for_team(TBA_EVENT_KEY, team_number)

        st.metric(label="Our Rank By Avg Pts", value=avg_pts_rank)
        st.metric(label="Our Rank By Rank Pts", value=frc_rank)

        st.metric(label="Avg Match Pts", value="{:.2f}".format(event_summary_dict['avg_total_pts']))
        st.metric(label="Climb Pts", value="{:.2f}".format(event_summary_dict['climb_pts']))

        st.metric(label="Avg Speaker Notes", value="{:.2f}".format(event_summary_dict['avg_notes_speaker']))
        st.metric(label="Avg Amp Notes", value="{:.2f}".format(event_summary_dict['avg_notes_amp']))

        st.metric(label="TBA Rank", value=team_tba_stats["rank"])
        st.metric(label="TBA OPR", value=team_tba_stats["opr"])
        st.metric(label="TBA DPR", value=team_tba_stats["dpr"])

    with st.container(height=200):
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

    with st.container(height=200):
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

    (auto_table, tele_table) = team_analysis.compute_scoring_table(summary, team_number)
    with st.container(height=250):
        st.subheader("Auto Accuracy")
        st.dataframe(
            data=auto_table.style.background_gradient(cmap=get_accuracy_colormap(), subset='accuracy', vmin=0.0,
                                                      vmax=1.0).format(precision=2), hide_index=True)
    with st.container(height=250):
        st.subheader("Teleop Accuracy")
        st.dataframe(
            data=tele_table.style.background_gradient(cmap=get_accuracy_colormap(), subset='accuracy', vmin=0.0,
                                                      vmax=1.0).format(precision=2), hide_index=True)

col2, col3, col4 = st.columns(3)

with col2:
    if len(filtered_summary) > 0:
        display_team(teams_to_compare[0], 0)
    else:
        st.header("Choose First Team")

with col3:
    if len(filtered_summary) > 1:
        display_team(teams_to_compare[1], 1)
    else:
        st.header("Choose 2nd Team")

with col4:
    if len(filtered_summary) > 2:
        display_team(teams_to_compare[2], 2)
    else:
        st.header("Choose 3rd Team")
