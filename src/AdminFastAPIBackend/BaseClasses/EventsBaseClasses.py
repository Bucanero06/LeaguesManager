"""Events"""
from typing import List, Optional

from pydantic import root_validator

from src.AdminFastAPIBackend.BaseClasses.BaseClasses import CoreModel, IDType
from src.AdminFastAPIBackend.BaseClasses.RulesBaseClasses import SeasonRules
from src.logger import setup_logger
logger = setup_logger(__name__)


class Season(CoreModel):
    sport_id: IDType
    league_id: Optional[IDType] = None
    #
    referee_ids: Optional[List[IDType]] = []
    team_ids: Optional[List[IDType]] = []
    game_ids: Optional[List[IDType]] = []  # todo autogenerate based on league/season rules

    # Rules
    rules: SeasonRules

class Game(CoreModel):
    score: Optional[List[IDType]] = None
    team_ids: Optional[List[IDType]] = None



