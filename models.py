from pydantic import BaseModel
from datetime import datetime
from enum import Enum, IntEnum


class ClimbEnum:
    SUCCESS = 'Success'
    SUCCESSPARTNER = 'Success with Partner'
    FAILED = 'Failed'
    NOTRY = 'NoTry'

    @classmethod
    def options(cls):
        return [ClimbEnum.SUCCESS,ClimbEnum.SUCCESSPARTNER,ClimbEnum.FAILED,ClimbEnum.NOTRY]

class PickupEnum:
    GROUND = 'Ground'
    SOURCE = 'Source'
    BOTH = 'Both'
    NONE = 'None'
    @classmethod
    def options(cls):
        return [PickupEnum.GROUND,PickupEnum.SOURCE,PickupEnum.BOTH,PickupEnum.NONE]

class EventEnum:
    ANDERSON = 'Anderson'
    CHARLESTON= 'Charleston'
    GWINNETT = 'Gwinnett'
    PCHCHAMPS = 'PCH Champs'

    @classmethod
    def options(cls):
        return [EventEnum.ANDERSON,EventEnum.CHARLESTON,EventEnum.PCHCHAMPS,EventEnum.GWINNETT]

class DriveEnum:
    SWERVE = 'Swerve'
    MECANUM = 'Mecanum'
    TANK = 'Tank'
    OTHER = 'Other'
#prefstart
    @classmethod
    def options(cls):
        return [DriveEnum.SWERVE,DriveEnum.MECANUM,DriveEnum.TANK,DriveEnum.OTHER]

class CanClimbEnum:
    YES = 'Yes'
    YESPARTNER = 'Yes with a Partner'
    NO = 'No'
    @classmethod
    def options(cls):
        return [CanClimbEnum.YES,CanClimbEnum.YESPARTNER,CanClimbEnum.NO]

class StartLocEnum:
    AMP = 'Amp side'
    MIDDLE = 'Middle'
    LANE = 'Lane side'

    @classmethod
    def options(cls):
        return [StartLocEnum.AMP, StartLocEnum.MIDDLE, StartLocEnum.LANE]

class ShotLocEnum:
    SUBWOOFER = 'Subwoofer'
    PODIUM = 'Podium'
    MIDDLE = 'Middle'
    MIDFIELD = 'Midfield'

    @classmethod
    def options(cls):
        return [ShotLocEnum.SUBWOOFER,ShotLocEnum.PODIUM,ShotLocEnum.MIDDLE,ShotLocEnum.MIDFIELD]

class Matches:
    @staticmethod
    def make_matches():
        matches = []
        for i in range(1,101):
            matches.append('Q'+str(i))
        for i in range(1,14):
            matches.append('P'+str(i))
        for i in range(1,4):
            matches.append('F'+str(i))
        return matches

class ScoutingRecord(BaseModel):
    tstamp: str = datetime.now().isoformat()
    team_number: int = 0
    match_number: str = ''
    scouter_name: str = ''
    event_name: str = ''
    notes_speaker_auto: int = 0
    notes_amp_auto: int = 0
    speaker_subwoofer_completed_auto: int = 0 #neither/scored/attempted in the current sheet for these
    speaker_subwoofer_attempted_auto: int = 0
    speaker_podium_completed_auto: int = 0
    speaker_podium_attempted_auto: int = 0
    speaker_medium_completed_auto: int = 0
    speaker_medium_attempted_auto: int = 0
    speaker_midfield_completed_auto: int = 0
    speaker_midfield_attempted_auto: int = 0
    robot_disabled_time: int = 0
    robot_speed: float = 0.0
    notes_speaker_teleop: int = 0
    notes_amp_teleop: int = 0
    speaker_subwoofer_completed_teleop: int = 0  #neither/scored/attempted in the current sheet for these
    speaker_subwoofer_attempted_teleop: int = 0
    speaker_podium_completed_teleop: int = 0
    speaker_podium_attempted_teleop: int = 0
    speaker_medium_completed_teleop: int = 0
    speaker_medium_attempted_teleop: int = 0
    speaker_midfield_completed_teleop: int = 0
    speaker_midfield_attempted_teleop: int = 0
    robot_pickup: str = PickupEnum.SOURCE
    climb: str = ClimbEnum.NOTRY
    team_present: bool = False
    mobility: bool = False
    alliance_coop: bool = False
    park: bool = False
    high_note: bool = False
    trap: bool = False
    mobility: bool = False
    rps: int = 0
    fouls: int = 0
    defense_rating: int = 0
    defense_forced_penalties: int = 0
    strategy: str = ''  #did they employ a strategy that might exaggerate their stats
    notes: str = ''


    def calc_fields(self):
        #note: attempted means 'how many misses' not how many misses plus successes'
        self.notes_speaker_teleop = self.speaker_subwoofer_completed_teleop +\
                                    self.speaker_podium_completed_teleop +\
                                    self.speaker_medium_completed_teleop + self.speaker_midfield_completed_teleop
    def as_tuple(self):
        return list(self.model_dump().values())


    @staticmethod
    def snake_column_headers():
        return ScoutingRecord.__fields__.keys()

    @staticmethod
    def dot_column_headers():
        return [ f.replace('_','.') for f in ScoutingRecord.snake_column_headers() ]

class PitScoutingRecord(BaseModel):
    tstamp: str = datetime.now().isoformat()
    team_number: int = 0
    scouter_name: str = ''
    event_name: str = ''
    robot_weight: float = 0.0
    robot_width: float = 0.0
    robot_length: float = 0.0
    under_stage: bool = False
    robot_drive: str = DriveEnum.TANK
    climb: str = CanClimbEnum.NO
    trap: bool = False
    pref_start: str = StartLocEnum.MIDDLE
    robot_pickup: str = PickupEnum.NONE
    score_abilities: str = ShotLocEnum.SUBWOOFER
    pref_shoot: str = ShotLocEnum.SUBWOOFER
    autos: str = ''
    strategy: str = ''  #did they employ a strategy that might exaggerate their stats
    notes: str = ''

    def as_tuple(self):
        return list(self.model_dump().values())


    @staticmethod
    def snake_column_headers():
        return PitScoutingRecord.__fields__.keys()

    @staticmethod
    def dot_column_headers():
        return [ f.replace('_','.') for f in PitScoutingRecord.snake_column_headers() ]

