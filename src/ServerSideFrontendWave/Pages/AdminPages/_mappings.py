from src.BaseClasses.EntitiesBaseClasses import Sport, League, Team
from src.BaseClasses.EventsBaseClasses import Season

LEAGUE_MANAGER_ITEM_NAME_LIST = ["sport", "league", "season", "team"]
ITEM_NAME_TO_COLLECTION_NAME_MAPPING = {
    "sport": "sports",
    "league": "leagues",
    "season": "seasons",
    "team": "teams",
}


# Map for the new item type
ITEM_NAME_TO_PYDANTIC_MODEL_MAP = {
    "sport": Sport,
    "league": League,
    "season": Season,
    "team": Team,
}

LEAGUE_MANAGER_ITEMS_LIST = [ITEM_NAME_TO_COLLECTION_NAME_MAPPING[item] for item in LEAGUE_MANAGER_ITEM_NAME_LIST]



