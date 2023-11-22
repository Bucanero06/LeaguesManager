import firebase_admin
from fastapi import FastAPI
from firebase_admin import credentials, firestore, auth
from google.rpc.http_pb2 import HttpResponse

from src.ServerSideFrontendWave.AdminFirestoreOperations import AdminFirestoreClient
from src.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI()
cred = credentials.Certificate("...")
db = firestore.client(app=firebase_admin.initialize_app(cred))
admin_firestore_client = AdminFirestoreClient(db=db)



# Validate Firebase User Token (Backend)
def verify_user_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        return uid
    except Exception as e:
        return HttpResponse(status_code=403, detail="Could not validate credentials or token expired.",
                                headers={"WWW-Authenticate": "Bearer"})


# add the routers
from src.AdminFastAPIBackend.Routes import AdminManualRoutes

app.include_router(AdminManualRoutes.router)



if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)
    #

    """
    For interacting through the admin league interface:
      The input is going to be based on the available options under the sport, league, season, and Teams
      Although you can define lower abstractions at any time and in any order, a straight forward way to arrive at the
          end goal of setting a working season is to define the sport, league, season, and optionally Teams in that
          order. Teams are also affected by the abstraction admin rules and Users so they can be defined at any time
          prior to the season starting. Opt in to have all this automated by the system (analytical-package) or do it
          manually.
    """
    # todo: Create New Sport (Soccer),  League (Monday League), Season (Summer 1 2023)
    #   Set rules for max teams, players/team, games/season or per team/season , use algorymths to set up games based on parametersetc
    #       *useful, set temporary schedule based on parameters, then if when season starts and teams are not full, then use algorymths to set up games based on new parameters
    # todo: User Use cases:
    #  * User signs up, registers team, and send invites to players which will create temporary accounts
    #       space in the team must be available
    #  * User signs up, registers as a player, then requests to join a team (maybe we do private/public teams idk)
    #     space in the team must be available, also if team is already registered and paid
    #  *Note* When team captain, creates team, they can choose to pay for the team which will be cheaper in total if full team, or they can select pay per player and only choose to pay for those who they want to for, however the diff in the plan's total needs to be fullfilled by other players. A designated time before the season they must pay either the team or per player prices.
    #       This means if new player is join
