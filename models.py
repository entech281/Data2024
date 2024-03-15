from pydantic import BaseModel
from datetime import datetime
from enum import Enum, IntEnum

class ClimbEnum:
    SUCCESS = 'Success'
    FAILED = 'Failed'
    NOTRY = 'NoTry'

    @classmethod
    def options(cls):
        return [ClimbEnum.SUCCESS,ClimbEnum.FAILED,ClimbEnum.NOTRY]

class PickupEnum:
    GROUND = 'Ground'
    SOURCE = 'Source'
    BOTH = 'Both'

    @classmethod
    def options(cls):
        return [PickupEnum.GROUND,PickupEnum.SOURCE,PickupEnum.BOTH]


class ScoutingRecord(BaseModel):
    tstamp: str = datetime.now().isoformat()
    team_number: int = 0
    match_number: str = ''
    scouter_name: str = ''
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
    pickup: str = PickupEnum.SOURCE
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
    def dot_column_headers():
        return [ f.replace('_','.') for f in ScoutingRecord.__fields__.keys() ]



