import pandas as pd
import numpy as np


def load_2024_data():
    raw_data = pd.read_csv("281 2024 scouting Data - Form Responses 1.csv")
    analyzed_data = team_analyze(raw_data)
    summary_data = team_summary(analyzed_data)
    return (
        analyzed_data,
        summary_data
    )

def team_summary(analzyed_data):
    team_summary = analzyed_data.groupby('team_number').agg(
        max_telop=('teleop.pts', 'max'),
        avg_telop=('teleop.pts', 'mean'),
        max_auto=('auto.pts', 'max'),
        avg_auto=('auto.pts', 'mean'),
        max_total_pts=('total.pts', 'max'),
        avg_total_pts=('total.pts', 'mean'),
        max_notes_speaker=('total.notes.speaker', 'max'),
        avg_notes_speaker=('total.notes.speaker', 'mean'),
        max_notes_amp=('total.notes.amp', 'max'),
        avg_notes_amp=('total.notes.amp', 'mean'),
        #reliability=('reliability', 'mean'),
        rps=('rp.pts','mean'),
        avg_speed=('fast.pts','mean')
    )

    team_summary = team_summary.sort_values(by='avg_total_pts', ascending=False).reset_index()
    return team_summary

def team_analyze(all_data):
    # rename columns to shorter better names
    all_data['tstamp'] = pd.to_datetime(all_data.Timestamp,errors='ignore')

    all_data = all_data.rename(columns={
        'Team Number': 'team.number',
        'Match Number (Ex. Q42)': 'match.number',
        'Mobility': 'mobility',
        'Scouter Name': 'scouter.name',
        'Total Notes in Speaker Auto': 'notes.speaker.auto',
        'Total Notes in Amp Auto': 'notes.amp.auto',
        'Notes in Auto': 'speaker.reliability.auto',
        'Alliance Co-op bonus': 'alliance.coop',
        'Pickup?': 'robot.pickup',
        'How many seconds were they disabled for': 'robot.disabled.time',
        'How many seconds to cross the whole field without interruption ': 'robot.speed',
        'Total Notes in Speaker Teleop': 'notes.speaker.teleop',
        'Total Notes in Amp Teleop': 'notes.amp.auto',
        'Notes in Tele-op': 'speaker.reliability.teleop',
        'Park?': 'park',
        'Climb?': 'climb',
        'Trap?': 'trap',
        'Fouls': 'fouls',
        'Team RPs': 'rps',
        'Did they employ a strategy that might exaggerate their stats?': 'strategy.impact',
        'General Notes (Separate statements with ;)': 'general.notes'

    })
    all_data['team.number'] = pd.to_numeric(all_data["team.number"],errors='ignore')
    all_data = all_data.drop(columns=['scouter.name'])

    base_data = all_data.fillna(0)

    base_data['rp.pts'] = base_data['rps']

    base_data['total.notes.speaker'] = base_data['notes.speaker.auto'] + base_data['notes.speaker.teleop']

    base_data['total.notes.amp'] = base_data['notes.amp.auto'] + base_data['notes.amp.teleop']

    base_data['mobility.pts'] = np.where ( base_data['mobility'] == 'Yes', 3.0, 0.0 )

    base_data['trap.pts'] = np.where ( base_data['trap'] == 'Yes', 5.0, 0.0)

    base_data['park.pts'] = np.where ( base_data['park'] == 'Yes', 2.0, 0.0)

    def choose_from_map(choice,choices,default):
        if choice in choices.keys():
            return choices.get(choice)
        else:
            return default

    #compute points for docking during auto

    def calc_fast_pts(row):
        #switch(Data!U2,"Fast",3,"Average",2,"Slow",1,0))
        base_data['fast.pts'] = base_data['robot.speed'] / 54.270833333
    base_data['fast.pts'] =base_data.apply(calc_fast_pts,axis=1)

    def calc_auto_docking_pts(row):
        return choose_from_map(row['climb'], {
            'Yes': 3.0,
            'Yes; with another robot': 3.0,
        }, 0.0)
    base_data['climb.pts'] = base_data.apply(calc_auto_docking_pts, axis=1)

    base_data['teleop.pts']= base_data['total.speaker.teleop']*2.0 + \
            base_data['total.amp.teleop']*1.0 + \
            base_data['climb.pts'] + \
            base_data['trap.pts'] + \
            base_data['park.pts']

    base_data['auto.pts']= base_data['total.speaker.auto']*5.0 + \
            base_data['total.amp.auto']*2.0 + \
            base_data['mobility.pts']

    base_data['total.pts']= base_data['auto.pts'] + \
            base_data['teleop.pts']

    base_data['speaker.pts']= base_data['total.speaker.auto']*5.0 + \
            base_data['total.speaker.teleop']*2.0

    base_data['amp.pts']= base_data['total.amp.auto']*2.0 + \
            base_data['total.amp.teleop']*1.0

    return base_data