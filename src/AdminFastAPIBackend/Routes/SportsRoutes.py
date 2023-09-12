
'''Sports CRUD'''
from firebase_admin import firestore

from src.BaseClasses.EntitiesBaseClasses import Sport
from src.ServerSideFrontendWave.AdminFirestoreOperations import AdminFirestoreClient
from src.logger import setup_logger
# import route dependencies instead of creating an app
from fastapi import APIRouter, HTTPException, Body

router = APIRouter()
logger = setup_logger(__name__)

db = firestore.client()
admin_firestore_client = AdminFirestoreClient(db=db)

@router.post("/sports/", tags=["sports", "ADMIN-CRUD"])
def create_sport(sport: Sport):
    return admin_firestore_client.sports_client.create(sport)


@router.get("/sports/{sport_id}", tags=["sports", "ADMIN-CRUD"])
def get_sport(sport_id: str):
    sport = admin_firestore_client.sports_client.get(sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    return sport


@router.put("/sports/{sport_id}", tags=["sports", "ADMIN-CRUD"])
def update_sport(sport_id: str, updated_data: dict = Body(...)):
    sport = admin_firestore_client.sports_client.update(sport_id, updated_data)
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    return sport


@router.delete("/sports/{sport_id}", tags=["sports", "ADMIN-CRUD"])
def delete_sport(sport_id: str):
    admin_firestore_client.sports_client.delete(sport_id)
    return {"status": "deleted", "id": sport_id}


@router.get("/sports/", tags=["sports", "ADMIN-CRUD"])
def get_all_sports():
    return admin_firestore_client.sports_client.get_all()
