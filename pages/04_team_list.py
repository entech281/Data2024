import streamlit as st
import team_analysis
import plotly.express as px
import gsheet_backend
import plotly.graph_objects as go

st.set_page_config(layout="wide")
CACHE_SECONDS = 60
SECRETS = st.secrets["gsheets"]


# TODO: duplicated tons
@st.cache_data(ttl=CACHE_SECONDS)
def load_match_data():
    raw_data = gsheet_backend.get_match_data(SECRETS)
    return team_analysis.analyze(raw_data)


(analyzed, summary) = load_match_data()


st.title("Team List")


summary_df = summary

if len(analyzed) == 0:
    st.header("No Data")
    st.stop()

top_teams = team_analysis.compute_top_team_summary(summary_df)

top_teams = top_teams.astype({'team.number': 'object'})
top_teams = top_teams.rename(columns={'team.number': 'team_number'})

max_rp = top_teams["rps"].max() * 1.25

bar = px.bar(top_teams, x='team_number', y=['teleop', 'auto'], title="Point For Top Teams", category_orders={
    'team_number': top_teams['team_number']
}).update_xaxes(type='category').update_layout(yaxis_title="Points")
bar.add_traces(go.Scatter(
    x=top_teams['team_number'],
    y=top_teams['rps'],
    mode='markers',
    yaxis="y2",
    marker=go.scatter.Marker(color="Red", size=12),
    name="rps")
)  # .update_yaxes(ranage=[0,max_rp])
bar.update_layout(yaxis2=dict(overlaying='y', side='right', range=[0, max_rp], showgrid=False))
st.plotly_chart(bar, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    # st.header("Teleop vs Auto")
    # plot = px.scatter(summary, x='avg_auto', y='avg_teleop', hover_name='team.number', size='avg_total_pts')
    # st.plotly_chart(plot)

    # st.header("Teleop vs Speed")
    # plot2 = px.scatter(summary, x='avg_speed', y='avg_teleop', hover_name='team.number', size='avg_total_pts')
    # st.plotly_chart(plot2)
    pass
with col2:
    # st.header("Speaker vs Amp")
    # plot2 = px.scatter(summary, x='avg_notes_speaker', y='avg_notes_amp', hover_name='team.number',
    #                   size='avg_total_pts')
    # st.plotly_chart(plot2)
    pass
