import config
import streamlit as st
config.configure(st.secrets) #TODO: how to ensure this happens no matter which page you start on?
import team_analysis
import controller
import tba
import gsheet_backend

st.set_page_config(layout="wide")
st.title("Team Compare")

tag_manager = gsheet_backend.get_tag_manager()
(analyzed, summary) = controller.get_all_joined_team_data()

teamlist = tba.get_all_pch_team_numbers()

teams_to_compare = st.multiselect("Select up to 3 Teams", key="compareteams", max_selections=3, options=teamlist,
                                  placeholder="")

filtered_summary = summary[summary["team_number"].isin(teams_to_compare)]



# TODO : ducpliated mostly from test foucs-- need to factor that out
def display_team(team_number, index):
    st.header(team_number)

    event_summary_df = summary[summary['team.number'] == team_number]
    team_pit_data = controller.pit_data_for_team(team_number)

    event_summary_dict = event_summary_df.to_dict(orient='records')[0]

    avg_pts_rank = str(event_summary_dict['rank_by_avg_pts'])
    frc_rank = str(event_summary_dict['frc_rank'])

    with st.container(height=200):
        st.multiselect("Tags", key='tags' + str(index), options=tag_manager.all_tag_list,
                       default=tag_manager.get_tags_for_team(team_number))
    with st.container(height=800):

        team_tba_stats = tba.get_tba_team_stats_for_team_current_event( team_number)

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
        if auto_table is not None:
            st.dataframe(
                data=auto_table.style.background_gradient(cmap=controller.get_accuracy_colormap(), subset='accuracy', vmin=0.0,
                                                          vmax=1.0).format(precision=2), hide_index=True)
        else:
            st.subheader("No played matches")
    with st.container(height=250):
        st.subheader("Teleop Accuracy")
        if tele_table is not None:
            st.dataframe(
                data=tele_table.style.background_gradient(cmap=controller.get_accuracy_colormap(), subset='accuracy', vmin=0.0,
                                                          vmax=1.0).format(precision=2), hide_index=True)
        else:
            st.subheader("No played matches")

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
