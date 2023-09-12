from pydantic import BaseModel, conint


class BaseRules(BaseModel):
    pass

class SeasonRules(BaseRules):
    max_teams: conint(ge=1) = 8  # Default value set to 8

class TeamRules(BaseRules):
    min_players_per_team: conint(ge=1) = 5  # Default value can be set, e.g., 5
    max_players_per_team: conint(ge=5) = 11  # Assuming a team can have a minimum of 5 and maximum of 11 players. Adjust as needed.

class LeagueRules(BaseRules):
    season: SeasonRules
    team: TeamRules
