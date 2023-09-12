from fastapi import APIRouter
from firebase_admin import firestore

from src.ServerSideFrontendWave.AdminFirestoreOperations import AdminFirestoreClient
from src.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()
db = firestore.client()
admin_firestore_client = AdminFirestoreClient(db=db)


@router.delete("/ALL/DELETE")
def delete_all_collections():
    logger.warning("Deleting all collections")
    admin_firestore_client.empty_all_collections()
    return {"status": "deleted all collections"}
