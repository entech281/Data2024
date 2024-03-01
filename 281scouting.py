import streamlit as st
import pandas as pd
import team_analysis
import plotly.express as px
import plotly.figure_factory as ff

from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    return team_analysis.load_2024_data()


st.title("281 2024 Scouting Data")
(analyzed, summary) = load_data()


analyzed_gb = GridOptionsBuilder.from_dataframe(analyzed)
analyzed_gb.configure_pagination(enabled=True,paginationAutoPageSize=True)
analyzed_gb.configure_default_column(groupable="true",filterable="true")
analyzed_gb.configure_grid_options(alwaysShowHorizontalScroll=True)
analyzed_gb.configure_side_bar(filters_panel=True)

summary_gb = GridOptionsBuilder.from_dataframe(summary)
summary_gb.configure_pagination(enabled=True,paginationAutoPageSize=True)
summary_gb.configure_default_column(groupable="true",filterable="true")
summary_gb.configure_grid_options(alwaysShowHorizontalScroll=True)
summary_gb.configure_side_bar(filters_panel=True)


st.header("Analyzed Match Data")
AgGrid(analyzed,
       gridOptions=analyzed_gb.build(),
       height=400,
       allow_unsafe_jscode=True,
       width="100%'",
       custom_css={ "#gridToolBar": { "padding-bottom": "0px !important", } }
)

st.header("Team Summary")


col1,col2= st.columns(2)
with col1:
    st.header("Teleop vs Auto")
    plot = px.scatter(summary, x='avg_auto', y='avg_telop', hover_name='team.number',size='avg_total_pts')
    st.plotly_chart(plot)

    st.header("Teleop vs Speed")
    plot2 = px.scatter(summary, x='avg_speed', y='avg_telop', hover_name='team.number',size='avg_total_pts')
    st.plotly_chart(plot2)

with col2:
    st.header("Speaker vs Amp")
    plot2 = px.scatter(summary, x='avg_notes_speaker', y='avg_notes_amp', hover_name='team.number',size='avg_total_pts')
    st.plotly_chart(plot2)


AgGrid(summary,
       gridOptions=summary_gb.build(),
       height=400,
       allow_unsafe_jscode=True,
       width="100%'",
       custom_css={ "#gridToolBar": { "padding-bottom": "0px !important", } }
)

st.header("Match Preditor")


red_col,blue_col= st.columns(2)
teamlist = list(summary['team_number'])
with red_col:
    st.header("Red Team")
    red_teams = st.multiselect("Red Team",key="redteams",max_selections=3,options=teamlist )

with blue_col:
    st.header("Blue Team")
    blue_teams = st.multiselect("Blue Team",key="blueteams",max_selections=3,options=teamlist )


if len(red_teams)==3 and len(blue_teams):
    blue_score = summary[ summary.team.number.isin (blue_teams)].sum()[ ['avg_auto','avg_teleop','avg_cones','avg_notes_speaker','avg_notes_amp','avg_total_pts'] ]
    red_score = summary[summary.team.number.isin(red_teams)].sum()[ ['avg_auto','avg_teleop','avg_cones','avg_notes_speaker','avg_notes_amp','avg_total_pts'] ]
    with red_col:
        st.write(red_score)
    with blue_col:
        st.write(blue_score)

st.header("Team Over Time")
focus_team = st.selectbox("Focus Team",options=teamlist)
if focus_team:
    perf_over_time = analyzed[ analyzed['team.number'] == focus_team   ]
    col3,col4,co15 =  st.columns(3)
    with col3:
        st.header("total pts over time")
        plot3 = px.scatter(perf_over_time, x='tstamp', y='total.pts')
        st.plotly_chart(plot3)
    with col4:
        st.header("speaker over time")
        plot4 = px.scatter(perf_over_time, x='tstamp', y='speaker.pts')
        st.plotly_chart(plot4)
    with co15:
        st.header("amp over time")
        plot5 = px.scatter(perf_over_time, x='tstamp', y='amp.pts')
        st.plotly_chart(plot5)
    st.write(perf_over_time)
