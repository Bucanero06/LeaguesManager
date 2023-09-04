from pydantic import BaseModel, conint


class SeasonRules(BaseModel):
    max_teams: conint(ge=1) = 8  # todo max can be default? or perhaps that pattern is not good. just an idea


class TeamRules(BaseModel):
    min_players_per_team: conint(ge=1)
    max_players_per_team: conint(ge=1)


class LeagueRules(BaseModel):
    season: SeasonRules
    team: TeamRules
