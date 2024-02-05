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
        'Team Number ': 'team_number_string',
        'Did they cross over the line?': 'auto_line',
        'How many cones scored [Top]': 'auto_cones_top',
        'How many cones scored [Middle]': 'auto_cones_middle',
        'How many cones scored [Bottom]': 'auto_cones_bottom',
        'How many cubes scored [Top]': 'auto_cubes_top',
        'How many cubes scored [Middle]': 'auto_cubes_middle',
        'How many cubes scored [Bottom]': 'auto_cubes_bottom',
        'Did they dock onto the station': 'auto_docked',
        'How many fouls committed by this team': 'fouls',
        'How many cones scored [Top ]': 'telop_cones_top',
        'How many cones scored [Middle].1': 'telop_cones_middle',
        'How many cones scored [Bottom].1': 'telop_cones_bottom',
        'How many cubes scored [Top ]': 'telop_cubes_top',
        'How many cubes scored [Middle].1': 'telop_cubes_middle',
        'How many cubes scored [Bottom].1': 'telop_cubes_bottom',
        "Where do their robot's capabilities allow them to score": 'scoring_areas',
        'Did they dock at the end': 'end_dock',
        'How fast was this robot': 'robot_speed',
        'Mechanical Failures ': 'failures',
        'How reliable was this robot (i.e. 4 completions/ 5 attempts)': 'reliability',
        'Special things about this bot': 'special_notes',
        'Blocks significant blocks made (significant obstruction of progress)': 'blocks',
        'Where do they pickup': 'pickup_loc'
    })
    all_data['team_number'] = pd.to_numeric(all_data.team_number_string,errors='ignore')
    all_data = all_data.drop(columns=['Email Address'])
    #fill out any number columns with NaN to zero
    #this way sums will work
    base_data = all_data.fillna(0)

    #add up cones and cubes
    base_data['total_cones'] = base_data['auto_cones_middle'] +  \
        base_data['auto_cones_top'] + base_data['auto_cones_bottom'] +  \
        base_data['telop_cones_middle'] + base_data['telop_cones_top'] + base_data['telop_cones_bottom']

    base_data['total_cubes'] = base_data['auto_cubes_middle'] + base_data['auto_cubes_top'] + \
          base_data['auto_cubes_bottom'] + base_data['telop_cones_middle'] +  \
          base_data['telop_cubes_top'] + base_data['telop_cubes_bottom']

    base_data['auto_line_pts'] = np.where ( base_data['auto_line'] == 'yes', 3.0, 0.0 )

    #this little function
    #lets you map values to numbers
    def choose_from_map(choice,choices,default):
        if choice in choices.keys():
            return choices.get(choice)
        else:
            return default

    #compute points for docking during auto
    def calc_auto_docking_pts(row):
        return choose_from_map(row['auto_docked'], {
            'Fully docked' : 12.0,
            'Partially (tilted)' : 8.0
        }, 0.0 )
    base_data['auto_dock_pts'] = base_data.apply(calc_auto_docking_pts,axis=1)

    def calc_fast_pts(row):
        #switch(Data!U2,"Fast",3,"Average",2,"Slow",1,0))
        return choose_from_map(row['robot_speed'], {
            'Fast' : 3.0,
            'Average' : 2.0,
            'Slow': 1.0
        }, 0.0 )
    base_data['fast_pts'] =base_data.apply(calc_fast_pts,axis=1)

    def calc_telop_dock_pts(row):
        #IF(Data!T2="Fully docked",10,IF(Data!T2="Partially (tilted)",6,0)))-5*Data!L2)
        return choose_from_map(row['robot_speed'], {
            'Fully docked' : 10.0,
            'Partially (tilted)' : 6.0
        }, 0.0 )
    base_data['telop_dock_pts'] = base_data.apply(calc_telop_dock_pts,axis=1)


    #SUM((Data!M2+Data!P2)*5+(Data!N2+Data!Q2)*3+(Data!O2+Data!R2)*2+IF(Data!T2="Fully docked",10,IF(Data!T2="Partially (tilted)",6,0)))-5*Data!L2)
    base_data['grid_pts']=  base_data['telop_cones_top']*5.0 + \
            base_data['telop_cones_middle']*3.0 + \
            base_data['telop_cones_bottom']*2.0 + \
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