from  models import ClimbEnum,PickupEnum
import pandas as pd
import numpy as np


def compute_top_team_summary(summary):
    top_teams = summary.sort_values(by='avg_total_pts', inplace=False, ascending=False)
    top_teams = top_teams.head(24)
    top_teams = top_teams[[ 'team.number', 'avg_teleop', 'avg_auto','rps']]
    top_teams = top_teams.rename(columns={
        'avg_teleop': 'teleop',
        'avg_auto': 'auto'
    })
    return top_teams
    
def compute_bar_scoring_summaries(analyzed_matches):
    pared_down = analyzed_matches
    pared_down['auto_scoring_summary'] = pared_down[[
        "amp.completed.auto",
        "speaker.subwoofer.completed.auto",
        "speaker.podium.completed.auto",
        "speaker.medium.completed.auto"
    ]].values.tolist()

    pared_down['total_amp_notes'] = pared_down['notes.amp.auto'] + pared_down['notes.amp.teleop']
    pared_down['total_spk_notes'] = pared_down['notes.speaker.auto'] + pared_down['notes.speaker.teleop']

    pared_down['teleop_scoring_summary'] = pared_down[[
        "amp.completed.teleop",
        "speaker.subwoofer.completed.teleop",
        "speaker.podium.completed.teleop",
        "speaker.medium.completed.teleop"
    ]].values.tolist()

    pared_down=  pared_down[[
        "tstamp",
        "team.number",
        'match.number',
        'total_amp_notes',
        'total_spk_notes',
        'teleop_scoring_summary',
        'auto_scoring_summary',
        'robot.disabled.time',
        'robot.speed',
        'robot.pickup',
        'climb',
        'team.present',
        'mobility',
        'alliance.coop',
        'park',
        'trap',
        'rp.pts',
        'fouls',
        'defense.rating',
        'defense.forced.penalties'
    ]]
    return pared_down



def get_comments_for_team(team_number, analyzed, comment_type):
    this_team_data = analyzed[ analyzed["team.number"] == team_number]
    this_team_data[comment_type].replace('',np.nan,inplace=True)
    return  this_team_data[comment_type].dropna().to_list()

def analyze(raw_data):
    analyzed_data = team_analyze(raw_data)
    summary_data = team_summary(analyzed_data)
    return (
        analyzed_data,
        summary_data
    )


def compute_scoring_table(team_summary,team_number):
    # TODO: probably a much more elegant way to columnize this!
    s = team_summary [ team_summary["team.number"] == team_number].to_dict(orient="records")[0]
 
    auto_data = pd.DataFrame(
        [
            {
                "Area": "Amp",
                "missed": s["amp_attempted_auto"],
                "made" : s["amp_completed_auto"]
            },
            {
                "Area": "Subwoofer",
                "missed": s["speaker_subwoofer_attempted_auto"],
                "made": s["speaker_subwoofer_completed_auto"]
            },
            {
                "Area": "Podium",
                "missed": s["speaker_podium_attempted_auto"],
                "made": s["speaker_podium_completed_auto"]
            },
            {
                "Area": "Other",
                "missed": s["speaker_medium_attempted_auto"],
                "made": s["speaker_medium_completed_auto"]
            }
        ]
    )
    tele_data = pd.DataFrame(
        [
            {
                "Area": "Amp",
                "missed": s["amp_attempted_teleop"],
                "made" : s["amp_completed_teleop"]
            },
            {
                "Area": "Subwoofer",
                "missed": s["speaker_subwoofer_attempted_teleop"],
                "made": s["speaker_subwoofer_completed_teleop"]
            },
            {
                "Area": "Podium",
                "missed": s["speaker_podium_attempted_teleop"],
                "made": s["speaker_podium_completed_teleop"]
            },
            {
                "Area": "Other",
                "missed": s["speaker_medium_attempted_teleop"],
                "made": s["speaker_medium_completed_teleop"]
            }
        ]
    )
    auto_data["attempts"] = auto_data["made"] + auto_data["missed"]
    auto_data["accuracy"] = auto_data["made"] / auto_data["attempts"]
    tele_data["attempts"] = tele_data["made"] + tele_data["missed"]
    tele_data["accuracy"] = tele_data["made"] / tele_data["attempts"]
    return (auto_data,tele_data)


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
        
        amp_attempted_auto=('amp.attempted.auto','sum'),
        amp_completed_auto=('amp.completed.auto', 'sum'),
        speaker_subwoofer_completed_auto=('speaker.subwoofer.completed.auto','sum'),
        speaker_subwoofer_attempted_auto=('speaker.subwoofer.attempted.auto','sum'),
        speaker_podium_completed_auto=('speaker.subwoofer.completed.auto','sum'),
        speaker_podium_attempted_auto=('speaker.podium.attempted.auto','sum'),
        speaker_medium_completed_auto=('speaker.subwoofer.completed.auto','sum'),
        speaker_medium_attempted_auto=('speaker.medium.attempted.auto','sum'),

        amp_attempted_teleop=('amp.attempted.teleop', 'sum'),
        amp_completed_teleop=('amp.completed.teleop', 'sum'),
        speaker_subwoofer_completed_teleop=('speaker.subwoofer.completed.teleop', 'sum'),
        speaker_subwoofer_attempted_teleop=('speaker.subwoofer.attempted.teleop', 'sum'),
        speaker_podium_completed_teleop=('speaker.subwoofer.completed.teleop', 'sum'),
        speaker_podium_attempted_teleop=('speaker.podium.attempted.teleop', 'sum'),
        speaker_medium_completed_teleop=('speaker.subwoofer.completed.teleop', 'sum'),
        speaker_medium_attempted_teleop=('speaker.medium.attempted.teleop', 'sum'),

        
        #sub_auto_acry=('sub.auto.acry','mean'),
        #mid_auto_acry=('mid.auto.acry','mean'),
        #pod_auto_acry=('pod.auto.acry','mean'),
        #sub_teleop_acry=('sub.teleop.acry','mean'),
        #mid_teleop_acry=('mid.teleop.acry','mean'),
        #pod_teleop_acry=('pod.teleop.acry','mean'),

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

    all_data.rename(inplace=True, columns={
        'rps':'rp.pts'
    })

    all_data['team.number'] = pd.to_numeric(all_data["team.number"],errors='ignore')
    all_data = all_data.drop(columns=['scouter.name'])

    base_data = all_data

    #base_data.rename(inplace=True, columns={
    #    'notes_speaker_auto': 'notes.speaker.auto',
    #    'notes_speaker_teleop': 'notes.speaker.teleop',
    #    'notes_amp_auto': 'notes.amp.auto',
    #    'notes_amp_teleop': 'notes.amp.teleop',
    #})

    #base_data["total.notes.attempted.auto"] = base_data["amp.attempted.auto"] + base_data["speaker.subwoofer.attempted.auto"] + base_data["speaker.podium.attempted.auto"] + base_data["speaker.podium.attempted.auto"]

    #base_data["total.notes.attempted.teleop"] = base_data["amp.attempted.teleop"] + base_data["speaker.subwoofer.attempted.teleop"] + base_data["speaker.podium.attempted.teleop"] + base_data["speaker.medium.attempted.teleop"]
    #base_data["notes.completed.teleop"] = base_data["amp.completed.teleop"] + base_data[ "speaker.subwoofer.completed.teleop"] + base_data["speaker.podium.completed.teleop"] + base_data[ "speaker.medium.completed.teleop"]
    #base_data["total.notes.attempted"] = base_data["total.notes.attempted.auto"]  + base_data["total.notes.attempted.teleop"] 
    #base_data["total.notes.completed"] = base_data["total.notes.completed.auto"]  + base_data["total.notes.completed.teleop"] 
    
    #base_data["notes.attempted.amp"] = base_data["amp.attempted.auto"] +  base_data["amp.attempted.teleop"]
    #base_data["notes.attempted.sub"] =base_data["speaker.subwoofer.attempted.auto"] +  base_data["speaker.subwoofer.attempted.teleop"]
    #base_data["notes.attempted.pod"] =base_data["speaker.podium.attempted.auto"] + base_data[ "speaker.subwoofer.completed.teleop"]
    #base_data['Notes.attempted.mid'] = base_data["speaker.medium.attempted.auto"] + base_data[ "speaker.medium.completed.teleop"]
    
    #base_data["notes.completed.amp"] = base_data["amp.completed.auto"] +  base_data["amp.completed.teleop"]
    #base_data["notes.completed.sub"] =base_data["speaker.subwoofer.completed.auto"] +  base_data["speaker.subwoofer.completed.teleop"]
    #base_data["notes.completed.pod"] =base_data["speaker.podium.completed.auto"] + base_data[ "speaker.subwoofer.completed.teleop"]
    #base_data['Notes.completed.mid'] = base_data["speaker.medium.completed.auto"] + base_data[ "speaker.medium.completed.teleop"]
    
    base_data["notes.speaker.auto"] =  base_data[ "speaker.subwoofer.completed.auto"] + base_data["speaker.podium.completed.auto"] + base_data[ "speaker.medium.completed.auto"]
    base_data["notes.speaker.teleop"] = base_data[ "speaker.subwoofer.completed.teleop"] + base_data["speaker.podium.completed.teleop"] + base_data[ "speaker.medium.completed.teleop"]
    base_data["total.notes.speaker"] = base_data["notes.speaker.auto"] + base_data["notes.speaker.teleop"]
    base_data["total.notes.amp"] =  base_data["amp.completed.teleop"] +base_data["amp.completed.auto"]
    base_data["notes.completed.auto"] = base_data["notes.speaker.auto"] + base_data["amp.completed.auto"]
    base_data["notes.completed.teleop"] = base_data["notes.speaker.teleop"] + base_data["amp.completed.teleop"]
    base_data["notes.amp.teleop"] = base_data["amp.completed.teleop"]
    base_data["notes.amp.auto"] = base_data["amp.completed.auto"]
    base_data['total.notes.amp'] = base_data["amp.completed.auto"] + base_data["amp.completed.teleop"]

    base_data['mobility.pts'] = np.where ( base_data['mobility'] , 3.0, 0.0 )

    base_data['trap.pts'] = np.where ( base_data['trap'] , 5.0, 0.0)

    base_data['park.pts'] = np.where ( base_data['park'], 2.0, 0.0)

    base_data['coop.pts'] = np.where(base_data['alliance.coop'],1.0,0.0 )

    FIELD_LENGTH=54.270833333
    base_data['fast.pts'] = base_data['robot.speed']/FIELD_LENGTH


    def choose_from_map(choice,choices,default):
        if choice in choices.keys():
            return choices.get(choice)
        else:
            return default

    def calc_auto_docking_pts(row):
        return choose_from_map(row['climb'], {
           ClimbEnum.SUCCESS : 3.0,
        }, 0.0)
    base_data['climb.pts'] = base_data.apply(calc_auto_docking_pts, axis=1)


    #def calc_accuracy_row(row,completed_field_name, attempted_field_name):
    #    total_shots = row[completed_field_name] + row[attempted_field_name]
    #    if total_shots> 0:
    #        return row[completed_field_name]/total_shots
    #    else:
    #        return 0.0


    # AUTO RELIABILITY
    #def calc_sub_auto_acry(row):
    #    return calc_accuracy_row(row,'speaker.medium.completed.auto','speaker.subwoofer.attempted.auto')
    #base_data['sub.auto.acry'] =base_data.apply(calc_sub_auto_acry, axis=1)

    #def calc_mid_auto_acry(row):
    #    return calc_accuracy_row(row,'speaker.medium.completed.auto','speaker.medium.attempted.auto')
    #base_data['mid.auto.acry'] = base_data.apply(calc_mid_auto_acry, axis=1)

    #def calc_amp_auto_acry(row):
    #    return calc_accuracy_row(row,'amp.completed.auto','amp.attempted.auto')
    #base_data['pod.auto.acry'] = base_data.apply(calc_amp_auto_acry, axis=1)


    #def calc_pod_auto_acry(row):
    #    return calc_accuracy_row(row,'speaker.podium.completed.auto','speaker.podium.attempted.auto')
    #base_data['pod.auto.acry'] = base_data.apply(calc_pod_auto_acry, axis=1)


    #TELEOP RELIABILITY

    #def calc_amp_teleop_acry(row):
    #    return calc_accuracy_row(row,'amp.completed.teleop','amp.attempted.teleop')
    #base_data['pod.auto.acry'] = base_data.apply(calc_amp_teleop_acry, axis=1)

    #def calc_sub_teleop_acry(row):
    #    return calc_accuracy_row(row,'speaker.medium.completed.auto','speaker.subwoofer.attempted.teleop')
    #base_data['sub.teleop.acry'] = base_data.apply(calc_sub_teleop_acry, axis=1)

    #def calc_mid_teleop_acry(row):
    #    return calc_accuracy_row(row,'speaker.medium.completed.auto','speaker.medium.attempted.teleop')
    #base_data['mid.teleop.acry'] = base_data.apply(calc_mid_teleop_acry, axis=1)


    #def calc_pod_teleop_acry(row):
    #    return calc_accuracy_row(row, 'speaker.podium.completed.auto', 'speaker.podium.attempted.teleop')
    #base_data['pod.teleop.acry'] = base_data.apply(calc_pod_teleop_acry, axis=1)


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