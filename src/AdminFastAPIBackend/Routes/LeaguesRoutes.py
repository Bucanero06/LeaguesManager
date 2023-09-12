'''Leagues CRUD'''
# import route dependencies instead of creating an app
from fastapi import APIRouter, HTTPException, Body
from firebase_admin import credentials, firestore

from src.BaseClasses.EntitiesBaseClasses import League
from src.ServerSideFrontendWave.AdminFirestoreOperations import AdminFirestoreClient
from src.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()
cred = credentials.Certificate("onlythemotivated-c2c2e-b5f9ea606b36.json")
db = firestore.client()

admin_firestore_client = AdminFirestoreClient(db=db)


@router.post("/leagues/", tags=["leagues", "ADMIN-CRUD"])
def create_league(league: League):
    return admin_firestore_client.leagues_client.create(league)


@router.get("/leagues/{league_id}", tags=["leagues", "ADMIN-CRUD"])
def get_league(league_id: str):
    league = admin_firestore_client.leagues_client.get(league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league


@router.put("/leagues/{league_id}", tags=["leagues", "ADMIN-CRUD"])
def update_league(league_id: str, updated_data: dict = Body(...)):
    league = admin_firestore_client.leagues_client.update(league_id, updated_data)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league


@router.delete("/leagues/{league_id}", tags=["leagues", "ADMIN-CRUD"])
def delete_league(league_id: str):
    admin_firestore_client.leagues_client.delete(league_id)
    return {"status": "deleted", "id": league_id}


@router.get("/leagues/", tags=["leagues", "ADMIN-CRUD"])
def get_all_leagues():
    return admin_firestore_client.leagues_client.get_all()
