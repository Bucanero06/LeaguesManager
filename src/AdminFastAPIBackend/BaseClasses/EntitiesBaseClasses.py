"""Entities"""
from typing import List, Optional

from pydantic import root_validator, constr

from src.AdminFastAPIBackend.BaseClasses.BaseClasses import CoreModel, validate_id_constraints, IDType
from src.AdminFastAPIBackend.BaseClasses.RulesBaseClasses import LeagueRules, TeamRules
from src.logger import setup_logger

logger = setup_logger(__name__)


class Entity(CoreModel):
    """Entity names must be unique. They are used as Firestore IDs. While case-sensitive, spaces are ignored."""
    name: constr(min_length=2, max_length=25, regex=r'^[a-zA-Z]+$', strip_whitespace=True)


class Sport(Entity):
    """This value is referenced by other Models"""

    @root_validator
    def set_id(cls, values):
        values["id"] = validate_id_constraints(values["name"])
        return values


class Club(Entity):
    """For organizations owning teams, e.g., a soccer club with multiple teams in possibly multiple leagues."""
    manager_id: IDType
    #
    coach_ids: List[IDType] = None
    team_ids: List[IDType] = None
    player_ids: List[IDType] = None

    @root_validator
    def set_id(cls, values):
        values["id"] = validate_id_constraints(values["name"])
        return values


class Team(Entity):
    club_id: IDType
    sport_id: IDType
    league_id: IDType
    season_id: IDType
    #
    player_ids: List[IDType] = None
    #
    rules: TeamRules

    @root_validator
    def set_id(cls, values):
        values["id"] = validate_id_constraints(f'{values["sport_id"]}-{values["club_id"]}-{values["name"]}')
        return values


class League(Entity):
    sport_id: IDType
    season_ids: List[IDType] = None
    #
    rules: LeagueRules

    @root_validator
    def set_id(cls, values):
        values["id"] = validate_id_constraints(f'{values["sport_id"]}-{values["name"]}')
        return values