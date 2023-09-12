"""Events"""
from typing import List, Optional

from src.BaseClasses.BaseClasses import CoreModel, FirestoreIDType
from src.BaseClasses.RulesBaseClasses import SeasonRules
from src.logger import setup_logger

logger = setup_logger(__name__)


class Season(CoreModel):
    sport_id: FirestoreIDType
    league_id: Optional[FirestoreIDType] = None
    #
    referee_ids: Optional[List[FirestoreIDType]] = []
    team_ids: Optional[List[FirestoreIDType]] = []
    game_ids: Optional[List[FirestoreIDType]] = []  # todo autogenerate based on league/season rules

    # Rules
    rules: SeasonRules


class Game(CoreModel):
    score: Optional[List[FirestoreIDType]] = None
    team_ids: Optional[List[FirestoreIDType]] = None
