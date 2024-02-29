import pandas as pd
import numpy as np

def team_summary(analzyed_data):
    team_summary = analzyed_data.groupby('team_number').agg(
        max_grid=('grid_pts', 'max'),
        avg_grid=('grid_pts', 'mean'),
        max_telop=('telop_pts', 'max'),
        avg_telop=('telop_pts', 'mean'),
        max_auto=('auto_pts', 'max'),
        avg_auto=('auto_pts', 'mean'),
        max_total_pts=('total_pts', 'max'),
        avg_total_pts=('total_pts', 'mean'),
        reliability=('reliability', 'mean'),
        max_cones=('total_cones', 'max'),
        avg_cones=('total_cones', 'mean'),
        max_cubes=('total_cubes', 'max'),
        avg_cubes=('total_cubes', 'mean'),
        rps=('extra_ranking_point','mean'),
        avg_speed=('fast_pts','mean')
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
        'Notes in Auto': 'speaker.auto',
        'Alliance Co-op bonus': 'alliance.coop',
        'Pickup?': 'robot.pickup',
        'How many seconds were they disabled for': 'robot.disabled.time',
        'How many seconds to cross the whole field without interruption ': 'robot.speed',
        'Total Notes in Speaker Teleop': 'notes.speaker.teleop',
        'Total Notes in Amp Teleop': 'notes.amp.auto',
        'Notes in Tele-op': 'speaker.teleop',
        'Park?': 'park',
        'Climb?': 'climb',
        'Trap?': 'trap',
        'Fouls': 'fouls',
        'Team RPs': 'rps',
        'Did they employ a strategy that might exaggerate their stats?': 'strategy.impact',
        'General Notes (Separate statements with ;)': 'general.notes'

    })
    all_data['team.number'] = pd.to_numeric(all_data.team_number_string,errors='ignore')
    all_data = all_data.drop(columns=['scouter.name'])
    #fill out any number columns with NaN to zero
    #this way sums will work
    base_data = all_data.fillna(0)

    #add up cones and cubes
    base_data['total.speaker'] = base_data['total.speaker.auto'] + base_data['total.speaker.teleop']

    base_data['total.amp'] = base_data['total.amp.auto'] + base_data['total.amp.teleop']

    base_data['mobility.pts'] = np.where ( base_data['mobility'] == 'yes', 3.0, 0.0 )

    #this little function
    #lets you map values to numbers
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


    #SUM((Data!M2+Data!P2)*5+(Data!N2+Data!Q2)*3+(Data!O2+Data!R2)*2+IF(Data!T2="Fully docked",10,IF(Data!T2="Partially (tilted)",6,0)))-5*Data!L2)
    base_data['speaker.pts']= base_data['total.speaker.auto']*5.0 + \
            base_data['total.speaker.teleop']*2.0 + \
            base_data['telop_cubes_top']*5.0 + \
            base_data['telop_cubes_middle']*3.0 + \
            base_data['telop_cubes_bottom']*2.0

    base_data['telop_pts'] = base_data['grid_pts'] +base_data['telop_dock_pts']

    def calc_charge_pts(row):
        #IF(Data!K2="Fully docked",12,IF(Data!K2="Partially (tilted)",8,0))+IF(Data!T2="Fully docked",10,IF(Data!T2="Partially (tilted)",6,0)))
        return choose_from_map(row['robot_speed'], {
            'Fully docked' : 10.0,
            'Partially (tilted)' : 6.0
        }, 0.0 )
    base_data['charge_pts'] = base_data['auto_dock_pts'] + base_data['telop_dock_pts']

    def calc_ranking_point(row):
        if row['charge_pts'] > 28:
            return 1.0
        else:
            return 0
    base_data['extra_ranking_point'] = base_data.apply(calc_ranking_point,axis=1)

    base_data['auto_pts'] =  base_data['auto_line_pts'] + \
        base_data['auto_dock_pts'] + \
        base_data['auto_cones_top']*6.0 +\
        base_data['auto_cones_middle']*4.0 +\
        base_data['auto_cones_bottom']*3.0
    base_data['total_pts'] = base_data['telop_pts'] + base_data['auto_pts']

    return base_data