import streamlit as st
import team_analysis
import tba
import gsheet_backend
from ordered_set import OrderedSet


SECRETS = st.secrets["gsheets"]
tba.set_auth_key(st.secrets["tba"]["auth_key"])
teamlist = tba.get_all_pch_team_numbers()

st.set_page_config(layout="wide")
st.title("Alliance Selection")

CACHE_SECONDS = 60
@st.cache_data(ttl=CACHE_SECONDS)
def load_match_data():
    raw_data = gsheet_backend.get_match_data(SECRETS)
    return team_analysis.analyze(raw_data)

(analyzed, summary) = load_match_data()

available_teams = teamlist.copy()
col1, col2, col3, col4 = st.columns(4)

CELL_HEIGHT = 220
with col1:
    a8 = st.container(height=CELL_HEIGHT)
    a1 = st.container(height=CELL_HEIGHT)
with col2:
    a7 = st.container(height=CELL_HEIGHT)
    a2 = st.container(height=CELL_HEIGHT)
with col3:
    a6 = st.container(height=CELL_HEIGHT)
    a3 = st.container(height=CELL_HEIGHT)
with col4:
    a5 = st.container(height=CELL_HEIGHT)
    a4 = st.container(height=CELL_HEIGHT)


def alliance_builder(alliance_number):
    AL = str(alliance_number)
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Alliance %d EPA:" % alliance_number)
    with col2:
        d = st.empty()
    t = st.multiselect("Teams:", key="%sT" % AL, options=available_teams, max_selections=3, placeholder="Choose 3")

    # return (a,b,c,d)
    return (t, d)


# TODO: make with a loop
with a1:
    al1 = alliance_builder(1)
with a2:
    al2 = alliance_builder(2)
with a3:
    al3 = alliance_builder(3)
with a4:
    al4 = alliance_builder(4)
with a5:
    al5 = alliance_builder(5)
with a6:
    al6 = alliance_builder(6)
with a7:
    al7 = alliance_builder(7)
with a8:
    al8 = alliance_builder(8)


def get_selected_teams(alliance_obj):
    s = set(alliance_obj[0])
    return s


def get_all_selected_teams(alliance_list):
    s = set()
    for al in alliance_list:
        s.update(get_selected_teams(al))
    return s


def set_epa(alliance_obj, value):
    alliance_obj[1].markdown("**{0:0.2f}**".format(value))


available_teams_set = OrderedSet(available_teams)
taken_teams = get_all_selected_teams([al1, al2, al3, al4, al5, al6, al7, al8])

remaining_teams = available_teams_set - taken_teams

all_team_data = team_analysis.get_all_joined_team_data(SECRETS)
remaining_teams_df = all_team_data[all_team_data['team_number'].isin(remaining_teams)]

for a in [al1, al2, al3, al4, al5, al6, al7, al8]:
    score = team_analysis.get_epa_for_teams(summary, get_selected_teams(a))
    set_epa(a, score)

st.subheader("%d remaining Teams" % len(remaining_teams_df))
# print("df",remaining_teams_df.columns)
st.dataframe(data=remaining_teams_df, hide_index=True, column_config={
    'team_number': st.column_config.NumberColumn(label="Team", width="Small", format="%d"),
    'record': st.column_config.TextColumn(label="record", width="Small"),
    'tag_list': st.column_config.TextColumn(label="tags", width="Medium"),
    'rank': st.column_config.NumberColumn(label="rank", width="Small"),
    'rank_by_avg_pts': st.column_config.NumberColumn(label="epa rank", width="Small"),
    'robot.pickup': st.column_config.TextColumn(label="pickup", width="Small"),
    'robot.drive': st.column_config.TextColumn(label="drive", width="Small"),
    'robot.weight': st.column_config.TextColumn(label="weight", width="Small"),
    'avg_teleop': st.column_config.NumberColumn(label="avg_teleop", width="Small", format="%0.2f"),
    'avg_auto': st.column_config.NumberColumn(label="avg_auto", width="Small", format="%0.2f"),
    'avg_endgame': st.column_config.NumberColumn(label="avg_endgame", width="Small", format="%0.2f"),
    'avg_notes_speaker': st.column_config.NumberColumn(label="avg_notes_spk", width="Small", format="%0.2f"),
    'avg_notes_amp': st.column_config.NumberColumn(label="avg_notes_amp", width="Small", format="%0.2f"),
    'subwoofer_accuracy_teleop': st.column_config.NumberColumn(label="subwoof_acry_tele", width="Small",
                                                               format="%0.2f"),
    'podium_tele_accuracy': st.column_config.NumberColumn(label="podium_acry_tele", width="Small", format="%0.2f"),
    'amp_accuracy_teleop': st.column_config.NumberColumn(label="apm_acry_tele", width="Small", format="%0.2f")
}, column_order=(
    'team_number',
    'record',
    'tag_list',
    'rank',
    'rank_by_avg_pts',
    'robot.pickup',
    'robot.weight',
    'avg_teleop',
    'avg_auto',
    'avg_endgame',
    'avg_notes_speaker',
    'avg_notes_amp',
    'subwoofer_accuracy_teleop',
    'podium_tele_accuracy',
    'amp_accuracy_teleop'
))
