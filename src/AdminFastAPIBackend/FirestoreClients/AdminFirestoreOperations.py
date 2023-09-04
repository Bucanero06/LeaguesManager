from typing import TypeVar
from firebase_admin import firestore
from src.AdminFastAPIBackend.BaseClasses.EntitiesBaseClasses import Sport, Club, Team, League
from src.AdminFastAPIBackend.BaseClasses.EventsBaseClasses import Season, Game
from src.AdminFastAPIBackend.BaseClasses.UsersBaseClasses import Player
from src.AdminFastAPIBackend.FirestoreClients.FirestoreClient import FirestoreClient
from src.logger import setup_logger

logger = setup_logger(__name__)

T = TypeVar('T')  # Generic type variable for your models


class AdminFirestoreClient:
    """Currently a Singleton class for AdminFirestoreClient."""
    _instance = None

    def __new__(cls, db: firestore.client):
        # Singleton pattern ( dont forget that this accepts db as a parameter)
        if cls._instance is None:
            cls._instance = super(AdminFirestoreClient, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, db: firestore.client):
        self.sports_client = FirestoreClient(db=db, collection_name="sports", model_cls=Sport)
        self.clubs_client = FirestoreClient(db=db, collection_name="clubs", model_cls=Club)
        self.teams_client = FirestoreClient(db=db, collection_name="teams", model_cls=Team)
        self.leagues_client = FirestoreClient(db=db, collection_name="leagues", model_cls=League)
        self.seasons_client = FirestoreClient(db=db, collection_name="seasons", model_cls=Season)
        self.games_client = FirestoreClient(db=db, collection_name="games", model_cls=Game)
        self.players_client = FirestoreClient(db=db, collection_name="players", model_cls=Player)

    def empty_all_collections(self):
        self.sports_client.empty_collection()
        self.clubs_client.empty_collection()
        self.teams_client.empty_collection()
        self.leagues_client.empty_collection()
        self.seasons_client.empty_collection()
        self.games_client.empty_collection()
        self.players_client.empty_collection()


if __name__ == '__main__':
    exit('exiting because I have an exit() statement right under if __name__ == __main__')

    # Initialize the Firestore DB
    cred = credentials.Certificate("../onlythemotivated-c2c2e-b5f9ea606b36.json")
    # firebase_admin.initialize_app()
    db = firestore.client(
        app=firebase_admin.initialize_app(cred),
    )

    admin_firestore_client = AdminFirestoreClient(db=db)

    # Delete all collections
    admin_firestore_client.empty_all_collections()

    '''From Admin Perspective'''

    # >>> These are useful for manual admin changes/control
    #
    # > Create new sport, league, season
    sport_model = admin_firestore_client.sports_client.create(Sport(name="Soccer"))
    league_model = admin_firestore_client.leagues_client.create(League(name="Monday League", sport_id=sport_model.id))
    season_model = admin_firestore_client.seasons_client.create(Season(sport_id=sport_model.id))

    # # > Test the Leagues Client
    # # Test adding the season to the league. Changes League[season_ids] and Season[league_id, status=active]
    # league_model = admin_firestore_client.leagues_client.add_season_to_league(league_id=league_model.id,
    #                                                                           season_id=season_model.id)
    # # Test removing the season from the league. Changes League[season_ids] and Season[league_id, status=inactive]
    # league_model = admin_firestore_client.leagues_client.remove_season_from_league(league_id=league_model.id,
    #                                                                                season_id=season_model.id)
    # # Test the delete league method. Changes Season[league_id, status=archived], first add a season to the league
    # league_model = admin_firestore_client.leagues_client.add_season_to_league(league_id=league_model.id,
    #                                                                           season_id=season_model.id)
    # admin_firestore_client.leagues_client.delete(league_id=league_model.id, hard_delete_children=False)
    #
    # # > Test the Seasons Client
    league_model = admin_firestore_client.leagues_client.create(League(name="Monday League", sport_id=sport_model.id))
    league_model = admin_firestore_client.leagues_client.add_season_to_league(league_id=league_model.id,
                                                                              season_id=season_model.id)
    # Test adding a team to the season. Changes Season[team_ids]
    club_model = admin_firestore_client.clubs_client.create(Club(name="Admin Club", status='active'))
    club_model = admin_firestore_client.clubs_client.teams_client.create(
        Team(
            sport_id=league_model.sport_id,
            league_id=league_model.id,
            season_id=season_model.id,
            club_id=club_model.id,
            name="Admin Team",
        )
    )

    season_model = admin_firestore_client.seasons_client.add_team_to_season(season_id=season_model.id,
                                                                            team_id=club_model.team_ids[0])

    # Test User-Player-Club-Team-Season mechanics
    league_model = admin_firestore_client.leagues_client.create(League(name="Monday League", sport_id=sport_model.id))
    league_model = admin_firestore_client.leagues_client.add_season_to_league(league_id=league_model.id,
                                                                              season_id=season_model.id)
    # - Register as Player and give extra permissions to create club
    #   - Create Player ( without payment information but with forms filled out)
    #   - Update Player (payment information is required before so permissions need to be updated)
    # - Player (or by admin) creates Club (with payment information) with Player as owner
    # - Create a Team with Club as captain
    # - Add Team to Season
    # - Add other players to Team (combined steps like Player to FreeAgent)
    # - Generate Games for Season
    # - Add Referee to Game
