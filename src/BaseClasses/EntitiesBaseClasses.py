"""Entities"""
from typing import List

from pydantic import model_validator, constr

from src.BaseClasses.BaseClasses import CoreModel, FirestoreIDType
from src.BaseClasses.RulesBaseClasses import LeagueRules, TeamRules
from src.logger import setup_logger

logger = setup_logger(__name__)


class Entity(CoreModel):
    """Entity names must be unique. They are used as Firestore IDs. While case-sensitive, spaces are ignored."""
    name: constr(min_length=2, max_length=25, strip_whitespace=True)


class Sport(Entity):
    """This value is referenced by other Models"""

    @model_validator(mode="before")
    def set_id(cls, values):
        values["id"] = FirestoreIDType(value=values["name"])
        return values


class Club(Entity):
    """For organizations owning teams, e.g., a soccer club with multiple teams in possibly multiple leagues."""
    manager_id: FirestoreIDType
    #
    coach_ids: List[FirestoreIDType] = None
    team_ids: List[FirestoreIDType] = None
    player_ids: List[FirestoreIDType] = None

    @model_validator(mode="before")
    def set_id(cls, values):
        values["id"] = FirestoreIDType(value=values["name"])
        return values


class Team(Entity):
    club_id: FirestoreIDType
    sport_id: FirestoreIDType
    league_id: FirestoreIDType = None
    season_id: FirestoreIDType = None
    #
    player_ids: FirestoreIDType = None
    #
    rules: TeamRules = None

    @model_validator(mode="before")
    def set_id(cls, values):
        values["id"] = FirestoreIDType(f'{values["sport_id"]}-{values["club_id"]}-{values["name"]}')
        return values


class League(Entity):
    """
    #TODO FIXME THOUGHTS
    Form to create a new league
    League Name: {{league_name}}
    League Description: {{league_description}}
    League Logo: {{league_logo}}
    League Commissioner: {{league_commissioner}}
    League Teams: {{league_teams}}
    League Players: {{league_players}}
    League Games: {{league_games}}
    League Schedule: {{league_schedule}}
    League Stats: {{league_stats}}
    League Standings: {{league_standings}}
    League Settings: {{league_settings}}
    League Payments: {{league_payments}}
    League Seasons: {{league_season}}
    """
    sport_id: FirestoreIDType
    #
    season_ids: List[FirestoreIDType] = None
    #
    rules: LeagueRules = None

    @model_validator(mode="before")
    def set_id(cls, values):
        values["id"] = FirestoreIDType(f'{values["sport_id"]}-{values["name"]}')
        return values
