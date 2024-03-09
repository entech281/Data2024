import pandas as pd
import numpy as np


def load_2024_data():
    raw_data = pd.read_csv("281.03-09-2024-11am.Data.csv")

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
        'Notes in Auto [Subwoofer]': 'subwoofer.reliability.auto',
        'Notes in Auto [Podium]': 'podium.reliability.auto',
        'Notes in Auto [Middle]': 'middle.reliability.auto',
        'Notes in Auto [Midfield]': 'midfield.reliability.auto',
        'Alliance Co-op bonus': 'alliance.coop',
        'Pickup?': 'robot.pickup',
        'How many seconds were they disabled for': 'robot.disabled.time',
        'How many seconds to cross the whole field without interruption': 'robot.speed',
        'Total Notes in Speaker Teleop': 'notes.speaker.teleop',
        'Total Notes in Amp Teleop': 'notes.amp.teleop',
        'Notes in Tele-op [Subwoofer]': 'subwoofer.reliability.teleop',
        'Notes in Tele-op [Podium]': 'podium.reliability.teleop',
        'Notes in Tele-op [Middle]': 'middle.reliability.teleop',
        'Notes in Tele-op [Midfield]': 'midfield.reliability.teleop',
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
    print(base_data.columns)
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
        FIELD_LENGTH=54.270833333
        base_data['fast.pts'] =  pd.to_numeric(base_data['robot.speed'],errors='coerce').fillna(0)
        base_data['fast.pts'].replace([np.inf],0,inplace=True)
        base_data['fast.pts'] = base_data['fast.pts']/FIELD_LENGTH
        base_data['fast.pts'] = base_data['fast.pts'].astype(int)

    base_data['fast.pts'] =base_data.apply(calc_fast_pts,axis=1)

    def calc_auto_docking_pts(row):
        return choose_from_map(row['climb'], {
            'Yes': 3.0,
            'Yes; with another robot': 3.0,
        }, 0.0)
    base_data['climb.pts'] = base_data.apply(calc_auto_docking_pts, axis=1)

#AUTO RELIABILITY

    def calc_sub_auto_acry(row):
        return choose_from_map(row['subwoofer.reliability.auto'], choices={
            'Neither': 0.0,
            'Attempted': 1.0,
            'Scored': 2.0,
        }, default=0.0)

    base_data['sub.auto.acry'] = base_data.apply(calc_sub_auto_acry, axis=1)

    def calc_mid_auto_acry(row):
        return choose_from_map(row['middle.reliability.auto'], choices={
            'Neither': 0.0,
            'Attempted': 1.0,
            'Scored': 2.0,
        }, default=0.0)

    base_data['mid.auto.acry'] = base_data.apply(calc_mid_auto_acry, axis=1)

    def calc_mfld_auto_acry(row):
        return choose_from_map(row['midfield.reliability.auto'], choices={
            'Neither': 0.0,
            'Attempted': 1.0,
            'Scored': 2.0,
        }, default=0.0)

    base_data['mfld.auto.acry'] = base_data.apply(calc_mfld_auto_acry, axis=1)

    def calc_pod_auto_acry(row):
        return choose_from_map(row['podium.reliability.auto'], choices={
            'Neither': 0.0,
            'Attempted': 1.0,
            'Scored': 2.0,
        }, default=0.0)

    base_data['pod.auto.acry'] = base_data.apply(calc_pod_auto_acry, axis=1)


#TELEOP RELIABILITY

    def calc_sub_teleop_acry(row):
        return choose_from_map(row['subwoofer.reliability.teleop'], choices= {
            'Neither': 0.0,
            'Attempted': 1.0,
            'Scored': 2.0,
        }, default=0.0)
    base_data['sub.teleop.acry'] = base_data.apply(calc_sub_teleop_acry, axis=1)

    def calc_mid_teleop_acry(row):
        return choose_from_map(row['middle.reliability.teleop'], choices={
            'Neither': 0.0,
            'Attempted': 1.0,
            'Scored': 2.0,
        }, default=0.0)

    base_data['mid.teleop.acry'] = base_data.apply(calc_mid_teleop_acry, axis=1)

    def calc_mfld_teleop_acry(row):
        return choose_from_map(row['midfield.reliability.teleop'], choices={
            'Neither': 0.0,
            'Attempted': 1.0,
            'Scored': 2.0,
        }, default=0.0)

    base_data['mfld.teleop.acry'] = base_data.apply(calc_mfld_teleop_acry, axis=1)
    def calc_pod_teleop_acry(row):
        return choose_from_map(row['podium.reliability.teleop'], choices= {
            'Neither': 0.0,
            'Attempted': 1.0,
            'Scored': 2.0,
        }, default=0.0)

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

    return base_data

if __name__ == "__main__":
    (analyzed, summary) = load_2024_data()
    analyzed.to_csv('281-3-8-2024.csv')