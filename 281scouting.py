import streamlit as st
import pandas as pd
import team_analysis
import gsheet_backend
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import altair as alt
import os
from match_scouting_form import build_match_scouting_form
from pit_scouting_form import build_pit_scouting_form
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from models import EventEnum

st.set_page_config(layout="wide")
SECRETS = st.secrets["gsheets"]


if True:
    print("Using local mode")
    import localfile_backend as gsheet_backend
else:
    print("Reading gsheet. To use local mode, set environment using set LOCAL=true")
    import gsheet_backend

CACHE_SECONDS=30
@st.cache_data(ttl=CACHE_SECONDS)
def load_data():
    raw_data= gsheet_backend.get_match_data(SECRETS)
    return team_analysis.analyze(raw_data)


st.title("281 2024 Scouting Data")

(analyzed, summary) = load_data()
teamlist = list(summary['team.number'])


HAS_DATA = True

analyzed_gb = GridOptionsBuilder.from_dataframe(analyzed)
analyzed_gb.configure_pagination(enabled=True, paginationAutoPageSize=True)
analyzed_gb.configure_default_column(groupable="true", filterable="true", width=50)
analyzed_gb.configure_grid_options(alwaysShowHorizontalScroll=True)
analyzed_gb.configure_side_bar(filters_panel=True)

summary_gb = GridOptionsBuilder.from_dataframe(summary)
summary_gb.configure_pagination(enabled=True, paginationAutoPageSize=True)
summary_gb.configure_default_column(groupable="true", filterable="true")
summary_gb.configure_grid_options(alwaysShowHorizontalScroll=True)
summary_gb.configure_side_bar(filters_panel=True)


def build_team_focus_tab(analyzed,summary):
    if not HAS_DATA:
        st.header("No Data")
        return

    focus_team = st.selectbox("Look at  Team", options=teamlist)
    focus_event = st.selectbox("Look at Event", options=EventEnum.options())

    if focus_team:
        st.header("Team Details for %s" % focus_team)
        general_comments = team_analysis.get_comments_for_team(focus_team,analyzed,'notes')
        strategy_comments = team_analysis.get_comments_for_team(focus_team, analyzed, 'strategy')
        perf_over_time = analyzed[analyzed['team.number'] == focus_team]
        summary_row = summary [ summary['team.number'] == focus_team]

    if focus_event:
        st.header("Team Details for %s" % focus_event)
        perf_over_time = perf_over_time[perf_over_time['event.name'] == focus_event]
        event_summary_df = team_analysis.team_summary(perf_over_time)

    if len(event_summary_df) == 0:
        st.header("No Data")
    else:
        event_summary_dict = event_summary_df.to_dict(orient='records')[0]
        col1,col2,col3 = st.columns(3)
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

        st.header("scoring timeline")
        plot3 = px.bar(perf_over_time, x='match.number', y=['speaker.pts','amp.pts'])
        plot3.update_layout(height=300)
        st.plotly_chart(plot3)

        st.header("Strategy Notes")
        st.dataframe(strategy_comments)

        st.header("General Notes")
        st.dataframe(general_comments)




def build_defense_tab(analyzed,summary):
    if not HAS_DATA:
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
    if not HAS_DATA:
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
    if not HAS_DATA:
        st.header("No Data")
        return

    st.header("Team Summary")

    top_teams = team_analysis.compute_top_team_summary(summary)

    top_teams = top_teams.astype({'team.number': 'object'})
    top_teams = top_teams.rename(columns={'team.number': 'team_number'})

    bar = px.bar(top_teams, x='team_number', y=['teleop', 'auto'], category_orders={
        'team_number': top_teams['team_number']
    }).update_xaxes(type='category')
    bar.add_traces(go.Scatter(
        x=top_teams['team_number'],
        y=top_teams['rps'],
        mode='markers',
        marker=go.scatter.Marker(color="Red", size=12),
        name="rps")
    )
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

def build_match_tab():
    if not HAS_DATA:
        st.header("No Data")
        return
    st.header("Analyzed Match Data")
    st.text("Choose Filters")
    col1, col2, col3 = st.columns(3)
    filtered_data = analyzed
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

    st.header("{d} Matching matches".format(d=len(filtered_data)))

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
            "Auto: SPK POD MED MID",
            y_min=0,
            y_max=5
        ),
        'teleop_scoring_summary': st.column_config.BarChartColumn(
            "Tele: SPK POD MED MID",
            y_min=0,
            y_max=5
        ),

    })
    #AgGrid(filtered_data,
    #       gridOptions=analyzed_gb.build(),
    #       columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    #       height=400,
    #       allow_unsafe_jscode=True,
    #       width="100%'",
    #       custom_css={"#gridToolBar": {"padding-bottom": "0px !important", }}
    #       )

    st.header("Team Stats")
    filtered_summary = summary

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
        def make_accuracy_slider(field_name):
            MIN_ACCURACY = 0.0
            MAX_ACCURACY = 3.0
            return st.slider(field_name, MIN_ACCURACY, MAX_ACCURACY, (MIN_ACCURACY, MAX_ACCURACY))

        pod_teleop_acry = make_accuracy_slider('pod_teleop_acry')
        filtered_summary = filtered_summary[filtered_summary["pod_teleop_acry"] >= pod_teleop_acry[0]]
        filtered_summary = filtered_summary[filtered_summary["pod_teleop_acry"] <= pod_teleop_acry[1]]

    with col5:
        pass

    with col6:
        pass

    with col7:
        pass

    with col8:
        pass

    st.header("{d} Matching teams".format(d=len(filtered_summary)))
    AgGrid(filtered_summary,
           gridOptions=summary_gb.build(),
           columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
           height=800,
           allow_unsafe_jscode=True,
           width="100%'",
           custom_css={"#gridToolBar": {"padding-bottom": "0px !important", }}
           )


teams,match_data,defense, match_predictor,team_focus,match_scouting,pit_scouting = st.tabs(['Teams','Matches', 'Defense', 'Match Predictor','Team Focus','Match Scouting','Pit Scouting'])
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
