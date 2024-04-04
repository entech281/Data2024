import config
import streamlit as st
config.configure(st.secrets) #TODO: how to ensure this happens no matter which page you start on?
import numpy as np
import math
import controller
import team_analysis
import tba
from models import PickupEnum,DriveEnum
import gsheet_backend
from ordered_set import OrderedSet


st.set_page_config(layout="wide")
st.title("Alliance Selection")

tag_manager = gsheet_backend.get_tag_manager()
(analyzed, summary) = controller.load_match_data()

teamlist = tba.get_all_pch_team_numbers()


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

(analyzed_data, summary_data) = controller.get_all_joined_team_data()
all_team_data = summary_data
remaining_teams_df = all_team_data[all_team_data['team_number'].isin(remaining_teams)]

for a in [al1, al2, al3, al4, al5, al6, al7, al8]:
    score = team_analysis.get_epa_for_teams(summary, get_selected_teams(a))
    set_epa(a, score)

with st.expander("Expand To Show Filters"):

    def make_field_slider(df, field_name, label):
        min_val = 0.0
        max_val = max(df[field_name].max(), 1.0)
        if math.isnan(max_val):
            max_val = 1.0

        (min_v, max_v) = st.slider(label, min_val, max_val, (min_val, max_val))

        new_df = df[(df[field_name] >= min_v) | np.isnan(df[field_name])]
        new_df = new_df[(new_df[field_name] <= max_v) | np.isnan(new_df[field_name])]
        return new_df

    col1,col2,col3,col4 = st.columns(4)
    with col1:
        only_swerve = st.checkbox("Only Swerve?")
        if only_swerve == True:
            print("Filtering swerve")
            remaining_teams_df = remaining_teams_df[remaining_teams_df["robot.drive"]==DriveEnum.SWERVE]

        is_ground_pickup = st.checkbox("Only Ground Pickup?")
        if is_ground_pickup == True:
            print("Filtering ground")
            remaining_teams_df = remaining_teams_df[remaining_teams_df["robot.pickup"].isin([PickupEnum.GROUND,PickupEnum.BOTH]) ]


        has_tags = st.multiselect("Has All Tags", key="has_tags", options=tag_manager.all_tag_list,default=[])
        missing_tags = st.multiselect("Does Not Have Any of Tags", key="missing_tags", options=tag_manager.all_tag_list, default=[])

        def filter_has_tags_func(row):
            try:
                row_tags = set(row['tag_list'])
                if  len(row_tags)> 0 :
                    if row_tags.issuperset(has_tags):
                        return True
                    else:
                        return False
                else:
                    return False
            except TypeError:
                # probably nan
                return False
            return False

        def filter_doesnt_have_tags_func(row):
            try:
                row_tags = set(row['tag_list'])
                if  len(row_tags)> 0 :
                    missing_tag_set = set(missing_tags)
                    if row_tags & missing_tag_set:
                        return False
                    else:
                        return True
                else:
                    return True
            except TypeError:
                # probably nan
                return True
            return False

        if len(has_tags) > 0 :
            tag_f =remaining_teams_df.apply(filter_has_tags_func,axis=1)
            remaining_teams_df = remaining_teams_df[tag_f]

        if len(missing_tags) > 0:
            no_tag_f =  remaining_teams_df.apply(filter_doesnt_have_tags_func,axis=1)
            remaining_teams_df = remaining_teams_df[no_tag_f]

    with col2:
        remaining_teams_df = make_field_slider(remaining_teams_df,'total_fouls',"Total Fouls")
        remaining_teams_df = make_field_slider(remaining_teams_df, 'avg_disabled_seconds', "avg_disabled_seconds")
        remaining_teams_df = make_field_slider(remaining_teams_df, 'avg_teleop', "avg_teleop")


    with col3:
        remaining_teams_df = make_field_slider(remaining_teams_df, 'subwoofer_accuracy_teleop', "subwoofer_accuracy_teleop")
        remaining_teams_df = make_field_slider(remaining_teams_df, 'podium_accuracy_teleop', "podium_accuracy_teleop")
        remaining_teams_df = make_field_slider(remaining_teams_df, 'amp_accuracy_teleop', "amp_accuracy_teleop")

    with col4:
        remaining_teams_df = make_field_slider(remaining_teams_df, 'avg_notes_speaker', "avg_notes_speaker")
        emaining_teams_df = make_field_slider(remaining_teams_df, 'avg_notes_amp', "avg_notes_amp")
        remaining_teams_df = make_field_slider(remaining_teams_df, 'avg_auto', "avg_auto")


st.subheader("%d remaining Teams" % len(remaining_teams_df))




st.dataframe(data=remaining_teams_df, hide_index=True, column_config={
    'team_number': st.column_config.NumberColumn(label="Team", width="Small", format="%d"),
    'record': st.column_config.TextColumn(label="record", width="Small"),
    'tag_list': st.column_config.TextColumn(label="tags", width="Medium"),
    'rank': st.column_config.NumberColumn(label="rank", width="Small"),
    'rank_by_avg_pts': st.column_config.NumberColumn(label="epa rank", width="Small"),
    'robot.pickup': st.column_config.TextColumn(label="pickup", width="Small"),
    'robot.drive': st.column_config.TextColumn(label="drive", width="Small"),
    'robot.weight': st.column_config.TextColumn(label="weight", width="Small"),
    'avg_disabled_seconds': st.column_config.NumberColumn(label="avg_disabled_secs", width="Small", format="%0.2f"),
    'opr': st.column_config.NumberColumn(label="opr", width="Small", format="%0.2f"),
    'dpr': st.column_config.NumberColumn(label="dpr", width="Small", format="%0.2f"),
    'total_fouls': st.column_config.NumberColumn(label="total_fouls", width="Small", format="%d"),
    'avg_teleop': st.column_config.NumberColumn(label="avg_teleop", width="Small", format="%0.2f"),
    'avg_auto': st.column_config.NumberColumn(label="avg_auto", width="Small", format="%0.2f"),
    'avg_endgame': st.column_config.NumberColumn(label="avg_endgame", width="Small", format="%0.2f"),
    'avg_notes_speaker': st.column_config.NumberColumn(label="avg_notes_spk", width="Small", format="%0.2f"),
    'avg_notes_amp': st.column_config.NumberColumn(label="avg_notes_amp", width="Small", format="%0.2f"),
    'subwoofer_accuracy_teleop': st.column_config.NumberColumn(label="subwoof_acry_tele", width="Small",format="%0.2f"),
    'podium_accuracy_teleop': st.column_config.NumberColumn(label="podium_acry_tele", width="Small", format="%0.2f"),
    'amp_accuracy_teleop': st.column_config.NumberColumn(label="amp_acry_tele", width="Small", format="%0.2f")
}, column_order=(
    'team_number',
    'record',
    'tag_list',
    'rank',
    'rank_by_avg_pts',
    'robot.pickup',
    'robot.drive',
    'robot.weight',
    'avg_disabled_seconds',
    'opr',
    'dpr',
    'total_fouls',
    'avg_teleop',
    'avg_auto',
    'avg_endgame',
    'avg_notes_speaker',
    'avg_notes_amp',
    'subwoofer_accuracy_teleop',
    'podium_accuracy_teleop',
    'amp_accuracy_teleop'
))
