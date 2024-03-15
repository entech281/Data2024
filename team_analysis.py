from  models import ScoutingRecord
import pandas as pd
import numpy as np
import toml

def compute_top_team_summary(summary):
    top_teams = summary.sort_values(by='avg_total_pts', inplace=False, ascending=False)
    top_teams = top_teams.head(24)
    top_teams = top_teams[[ 'team.number', 'avg_teleop', 'avg_auto','rps']]
    top_teams = top_teams.rename(columns={
        'avg_teleop': 'teleop',
        'avg_auto': 'auto'
    })
    return top_teams

def get_comments_for_team(team_number, analyzed):
    this_team_data = analyzed[ analyzed["team.number"] == team_number]
    general_comments = this_team_data[['general.notes']].dropna()
    return general_comments

def analyze(raw_data):
    raw_data = get_match_data()

    analyzed_data = team_analyze(raw_data)
    summary_data = team_summary(analyzed_data)
    return (
        analyzed_data,
        summary_data
    )

def team_summary(analzyed_data):
    team_summary = analzyed_data.groupby('team.number').agg(
        max_teleop=('teleop.pts', 'max'),
        avg_teleop=('teleop.pts', 'mean'),
        max_auto=('auto.pts', 'max'),
        avg_auto=('auto.pts', 'mean'),
        max_total_pts=('total.pts', 'max'),
        avg_total_pts=('total.pts', 'mean'),
        max_notes_speaker=('total.notes.speaker', 'max'),
        avg_notes_speaker=('total.notes.speaker', 'mean'),
        max_notes_amp=('total.notes.amp', 'max'),
        avg_notes_amp=('total.notes.amp', 'mean'),
        sub_auto_acry=('sub.auto.acry','mean'),
        mid_auto_acry=('mid.auto.acry','mean'),
        mfld_auto_acry=('mfld.auto.acry','mean'),
        pod_auto_acry=('pod.auto.acry','mean'),
        sub_teleop_acry=('sub.teleop.acry','mean'),
        mid_teleop_acry=('mid.teleop.acry','mean'),
        mfld_teleop_acry=('mfld.teleop.acry','mean'),
        pod_teleop_acry=('pod.teleop.acry','mean'),
        rps=('rp.pts','sum'),
        avg_speed=('fast.pts','mean'),
        parks_pts=('park.pts','mean'),
        climb_pts=('climb.pts','mean'),
        mobility_pts=('mobility.pts','mean'),
        avg_coop_pts=('coop.pts','mean'),
        avg_endgame=('endgame.pts','mean')
    )
    team_summary['rank_by_avg_pts'] = team_summary[['avg_total_pts','avg_teleop']].apply(tuple,axis=1).rank(method='dense', ascending=False)
    team_summary['frc_rank'] = team_summary[
        ['rps','avg_coop_pts','avg_total_pts','avg_auto','avg_endgame']
    ].apply(tuple,axis=1).rank(method='dense',ascending=False)

    #ranking method
    # 1 raking points
    # 2 avg coopertision
    # 3 avg alliance match score without fouls
    # 4 avg alliance auto
    # 5 avg alliance endgame
    # 6 random


    team_summary = team_summary.sort_values(by='avg_total_pts', ascending=False).reset_index()
    team_summary['team.number'] = team_summary['team.number'].astype(int)

    return team_summary.fillna(0)

def team_analyze(all_data):
    # rename columns to shorter better names
    all_data['tstamp'] = pd.to_datetime(all_data.tstamp,errors='ignore')


    all_data['team.number'] = pd.to_numeric(all_data["team.number"],errors='ignore')
    all_data = all_data.drop(columns=['scouter_name'])
    #all_data['team.number'].replace([np.inf, np.nan], 0, inplace=True)
    #all_data['team.number'] = all_data['team.number'].astype(int)
    base_data = all_data

    base_data.rename(inplace=True, columns={
        'notes_speaker_auto': 'notes.speaker.auto',
        'notes_speaker_teleop': 'notes.speaker.teleop',
        'notes_amp_auto': 'notes.amp.auto',
        'notes_amp_teleop': 'notes.amp.teleop',
    })

    base_data['total.notes.speaker'] = base_data['notes.speaker.auto'] + base_data['notes.speaker.teleop']

    base_data['total.notes.amp'] = base_data['notes.amp.auto'] + base_data['notes.amp.teleop']

    base_data['mobility.pts'] = np.where ( base_data['mobility'] , 3.0, 0.0 )

    base_data['trap.pts'] = np.where ( base_data['trap'] , 5.0, 0.0)

    base_data['park.pts'] = np.where ( base_data['park'], 2.0, 0.0)

    def choose_from_map(choice,choices,default):
        if choice in choices.keys():
            return choices.get(choice)
        else:
            return default

    #compute points for docking during auto

    FIELD_LENGTH=54.270833333
    #base_data['fast.pts'] =  pd.to_numeric(base_data['robot.speed'],errors='coerce').fillna(0)/FIELD_LENGTH
    base_data['fast.pts'] = 0
    def calc_coop_points(row):
        return choose_from_map(row['alliance_coop'], {
            True : 1.0
        }, 0.0)
    base_data['coop.pts'] = base_data.apply(calc_coop_points, axis=1)

    def calc_auto_docking_pts(row):
        return choose_from_map(row['climb'], {
            True: 3.0,
            #'Yes; with another robot': 3.0,
        }, 0.0)
    base_data['climb.pts'] = base_data.apply(calc_auto_docking_pts, axis=1)


    def calc_accuracy_row(row,field_name):
        return choose_from_map(row[field_name], choices={
            'Neither': 0.0,
            'Attempted': 1.0,
            'Scored': 2.0,
        }, default=0.0)

    # AUTO RELIABILITY
    def calc_sub_auto_acry(row):
        return calc_accuracy_row(row,'subwoofer.reliability.auto')
    base_data['sub.auto.acry'] = base_data.apply(calc_sub_auto_acry, axis=1)

    def calc_mid_auto_acry(row):
        return calc_accuracy_row(row,'middle.reliability.auto')
    base_data['mid.auto.acry'] = base_data.apply(calc_mid_auto_acry, axis=1)

    def calc_mfld_auto_acry(row):
        return calc_accuracy_row(row,'midfield.reliability.auto')
    base_data['mfld.auto.acry'] = base_data.apply(calc_mfld_auto_acry, axis=1)

    def calc_pod_auto_acry(row):
        return calc_accuracy_row(row,'podium.reliability.auto')
    base_data['pod.auto.acry'] = base_data.apply(calc_pod_auto_acry, axis=1)


    #TELEOP RELIABILITY

    def calc_sub_teleop_acry(row):
        return calc_accuracy_row(row,'subwoofer.reliability.teleop')
    base_data['sub.teleop.acry'] = base_data.apply(calc_sub_teleop_acry, axis=1)

    def calc_mid_teleop_acry(row):
        return calc_accuracy_row(row,'middle.reliability.teleop')
    base_data['mid.teleop.acry'] = base_data.apply(calc_mid_teleop_acry, axis=1)

    def calc_mfld_teleop_acry(row):
        return calc_accuracy_row(row,'midfield.reliability.teleop')

    base_data['mfld.teleop.acry'] = base_data.apply(calc_mfld_teleop_acry, axis=1)
    def calc_pod_teleop_acry(row):
        return calc_accuracy_row(row,'podium.reliability.teleop')
    base_data['pod.teleop.acry'] = base_data.apply(calc_pod_teleop_acry, axis=1)


    base_data['teleop.pts']= base_data['notes.speaker.teleop']*2.0 + \
            base_data['notes.amp.teleop']*1.0 + \
            base_data['climb.pts'] + \
            base_data['trap.pts'] + \
            base_data['park.pts']

    base_data['auto.pts']= base_data['notes.speaker.auto']*5.0 + \
            base_data['notes.amp.auto']*2.0 + \
            base_data['mobility.pts']

    base_data['total.pts']= base_data['auto.pts'] + \
            base_data['teleop.pts']

    base_data['speaker.pts']= base_data['notes.speaker.auto']*5.0 + \
            base_data['notes.speaker.teleop']*2.0

    base_data['amp.pts']= base_data['notes.amp.auto']*2.0 + \
            base_data['notes.amp.teleop']*1.0

    base_data['endgame.pts'] = base_data['climb.pts'] + base_data['trap.pts'] + base_data['park.pts']

    return base_data