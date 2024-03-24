import streamlit as st
import team_analysis
import plotly.express as px
import plotly.graph_objects as go
from  matplotlib.colors import LinearSegmentedColormap




def get_accuracy_colormap():
    c = ["darkred","red","lightcoral","white", "palegreen","green","darkgreen"]
    v = [0,.15,.4,.5,0.6,.9,1.]
    l = list(zip(v,c))
    cmap=LinearSegmentedColormap.from_list('rg',l, N=256)
    return cmap

import plotly.figure_factory as ff

from match_scouting_form import build_match_scouting_form
from pit_scouting_form import build_pit_scouting_form

st.set_page_config(layout="wide")
SECRETS = st.secrets["gsheets"]

LOCAL_MODE=False
if LOCAL_MODE:
    print("Using local mode")
    import localfile_backend as gsheet_backend
else:
    print("Reading gsheet. To use local mode, set environment using set LOCAL=true")
    import gsheet_backend

CACHE_SECONDS=30
@st.cache_data(ttl=CACHE_SECONDS)
def load_match_data():
    raw_data= gsheet_backend.get_match_data(SECRETS)
    return team_analysis.analyze(raw_data)

@st.cache_data(ttl=CACHE_SECONDS)
def load_pit_data():
    raw_data = gsheet_backend.get_pits_data(SECRETS)
    return raw_data


def pit_data_for_team(team_num):
    all_data = load_pit_data()
    team_data = all_data[ all_data['team.number'] == team_num]
    if len(team_data) > 0:
        return team_data.to_dict(orient='records')[0]
    else:
        return {}

st.title("281 2024 DCMP Scouting")

(analyzed, summary) = load_match_data()
pit_data = load_pit_data()
teamlist = list(summary['team.number'])


def write_markdown_list( vals):
    s = ""
    for v in vals:
        s += ("* " + v + "___" + "\n")
    return s

def build_team_focus_tab(analyzed,summary):
    analyzed_and_filtered = analyzed
    if len(analyzed_and_filtered) == 0:
        st.header("No Data")
        return

    focus_team = st.selectbox("Choose Team", options=teamlist)

    if focus_team:
        event_summary_df = team_analysis.team_summary(analyzed_and_filtered)
        analyzed_and_filtered = analyzed_and_filtered[ analyzed_and_filtered["team.number"] == focus_team]
        general_comments = team_analysis.get_comments_for_team(focus_team,analyzed,'notes')
        strategy_comments = team_analysis.get_comments_for_team(focus_team, analyzed, 'strategy')

        event_summary_df = event_summary_df [ event_summary_df['team.number'] == focus_team]
        team_pit_data = pit_data_for_team(focus_team)


    if len(event_summary_df) == 0:
        st.header("No Data")
    else:
        event_summary_dict = event_summary_df.to_dict(orient='records')[0]

        col1,col2,col3,col4,col5 = st.columns(5)
        with col1:
            avg_pts_rank = int(event_summary_dict['rank_by_avg_pts'])
            frc_rank = int(event_summary_dict['frc_rank'])
            st.metric(label="Rank By Avg Pts",value=avg_pts_rank)
            st.metric(label="Rank By Rank Pts", value=frc_rank)
            if avg_pts_rank > frc_rank:
                st.warning("OverRanked!",icon="⚠")

        with col2:
            st.metric(label="Avg Match Pts", value="{:.2f}".format(event_summary_dict['avg_total_pts']))
            st.metric(label="Climb Pts", value="{:.2f}".format(event_summary_dict['climb_pts']))

        with col3:
            st.metric(label="Avg Speaker Notes", value="{:.2f}".format(event_summary_dict['avg_notes_speaker']))
            st.metric(label="Avg Amp Notes", value="{:.2f}".format(event_summary_dict['avg_notes_amp']))

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

        (auto_table, tele_table) = team_analysis.compute_scoring_table(summary,focus_team)

        col1,col2= st.columns(2)
        with col1:
            st.subheader("Auto Accuracy")
            st.dataframe(
                data=auto_table.style.background_gradient(cmap=get_accuracy_colormap(),subset='accuracy',vmin=0.0,vmax=1.0).format(precision=2),hide_index=True)
        with col2:
            st.subheader("Teleop Accuracy")
            st.dataframe(data=tele_table.style.background_gradient(cmap=get_accuracy_colormap(),subset='accuracy',vmin=0.0,vmax=1.0).format(precision=2),hide_index=True)
        st.header("scoring timeline")
        plot3 = px.bar(analyzed_and_filtered, x='match.number', y=['notes.speaker.auto','notes.speaker.teleop','notes.amp.auto', 'notes.amp.teleop'])
        plot3.update_layout(height=300,yaxis_title="Notes Scored")
        st.plotly_chart(plot3)



        st.header("General Notes")
        st.markdown(write_markdown_list(general_comments))

        st.header("Strategy Notes")
        st.markdown(write_markdown_list(strategy_comments))


def build_defense_tab(analyzed,summary):
    if len(analyzed)==0:
        st.header("No Data")
        return
    focus_team = st.selectbox("Look at  Team", options=teamlist,key="defense_team")

    if focus_team:
        st.header("Team Details for %s" % focus_team)
        general_comments = team_analysis.get_comments_for_team(focus_team, analyzed, 'notes')
        perf_over_time = analyzed[analyzed['team.number'] == focus_team]
        summary_row = summary [ summary['team.number']== focus_team].to_dict(orient='records')[0]

        col1,col2 = st.columns(2)
        with col1:
            st.metric(label="Avg Speed",value="{:.2f}".format(summary_row['avg_speed']))
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

def build_match_predictor():
    if len(analyzed)==0:
        st.header("No Data")
        return

    st.header("Match Preditor")
    red_col, blue_col = st.columns(2)

    with red_col:
        st.header("Red Team")
        red_teams = st.multiselect("Red Team", key="redteams", max_selections=3, options=teamlist)

    with blue_col:
        st.header("Blue Team")
        blue_teams = st.multiselect("Blue Team", key="blueteams", max_selections=3, options=teamlist)

    if len(red_teams) == 3 and len(blue_teams) == 3:
        blue_score = summary[summary["team.number"].isin(blue_teams)].sum()[
            ['avg_auto', 'avg_teleop', 'avg_notes_speaker', 'avg_notes_amp', 'avg_total_pts']]
        red_score = summary[summary["team.number"].isin(red_teams)].sum()[
            ['avg_auto', 'avg_teleop', 'avg_notes_speaker', 'avg_notes_amp', 'avg_total_pts']]
        with red_col:
            st.write(red_score)
        with blue_col:
            st.write(blue_score)


def build_team_tab():
    if len(analyzed)==0:
        st.header("No Data")
        return

    st.header("Team Summary")
    summary_df = summary

    top_teams = team_analysis.compute_top_team_summary(summary_df)

    top_teams = top_teams.astype({'team.number': 'object'})
    top_teams = top_teams.rename(columns={'team.number': 'team_number'})

    max_rp = top_teams["rps"].max()*1.25

    bar = px.bar(top_teams, x='team_number', y=['teleop', 'auto'],title="Point For Top Teams", category_orders={
        'team_number': top_teams['team_number']
    }).update_xaxes(type='category').update_layout(yaxis_title="Points")
    bar.add_traces(go.Scatter(
        x=top_teams['team_number'],
        y=top_teams['rps'],
        mode='markers',
        yaxis="y2",
        marker=go.scatter.Marker(color="Red", size=12),
        name="rps")
    )   #.update_yaxes(ranage=[0,max_rp])
    bar.update_layout(yaxis2=dict(overlaying='y', side='right', range=[0,max_rp],showgrid=False))
    st.plotly_chart(bar, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.header("Teleop vs Auto")
        plot = px.scatter(summary, x='avg_auto', y='avg_teleop', hover_name='team.number', size='avg_total_pts')
        st.plotly_chart(plot)

        st.header("Teleop vs Speed")
        plot2 = px.scatter(summary, x='avg_speed', y='avg_teleop', hover_name='team.number', size='avg_total_pts')
        st.plotly_chart(plot2)

    with col2:
        st.header("Speaker vs Amp")
        plot2 = px.scatter(summary, x='avg_notes_speaker', y='avg_notes_amp', hover_name='team.number',
                           size='avg_total_pts')
        st.plotly_chart(plot2)

def build_pit_tab(pit_data):
    st.header("Pit Data")
    if len(pit_data)==0:
        st.header("No Data")
        return
    st.dataframe(data=pit_data,height=600,column_config={
        #a stacked bar here woudl be ideal!
        #these oculd also be over time which would be cool too
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

    }
    )

def build_match_tab():
    if len(analyzed)==0:
        st.header("No Data")
        return
    st.header("Analyzed Match Data")
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
        MAX_FOULS = max(analyzed["fouls"].max(),1)
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

    #see optoins here: https://docs.streamlit.io/library/api-reference/data/st.dataframe
    filtered_data_with_summary = team_analysis.compute_bar_scoring_summaries(filtered_data)
    st.dataframe(filtered_data_with_summary,use_container_width=True,hide_index=True,column_config={
        #a stacked bar here woudl be ideal!
        #these oculd also be over time which would be cool too
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
        'auto_scoring_summary':st.column_config.BarChartColumn(
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


match_scouting,pit_scouting, team_focus,teams,match_data,defense, match_predictor,pit_data_tab = st.tabs([
   'Match Scouting','Pit Scouting','Team Detail','Teams' ,'Matches', 'Defense', 'Match Predictor','Pit Data'])
with teams:
    build_team_tab()

with match_data:
    build_match_tab()

with defense:
    build_defense_tab(analyzed,summary)
with team_focus:
    build_team_focus_tab(analyzed,summary)

with match_predictor:
    build_match_predictor()

with match_scouting:
    build_match_scouting_form()

with pit_scouting:
    build_pit_scouting_form()

with pit_data_tab:
    build_pit_tab(pit_data)
