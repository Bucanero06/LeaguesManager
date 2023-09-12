import asyncio
import datetime
import threading

from firebase_admin import firestore
from h2o_wave import Q

from src.ServerSideFrontendWave.AdminFirestoreOperations import AdminFirestoreClient
from src.ServerSideFrontendWave.Pages.AdminPages._mappings import LEAGUE_MANAGER_ITEMS_LIST
from src.ServerSideFrontendWave._globals import module_global_collection_cache

cache_lock = threading.Lock()

db = firestore.client()
admin_firestore_client = AdminFirestoreClient(db)


def create_on_snapshot_callback(collection_name: str):
    def on_snapshot(doc_snapshot, changes, read_time):
        with cache_lock:
            print(f'{doc_snapshot = }')
            module_global_collection_cache[collection_name] = {doc.id: doc.to_dict() for doc in doc_snapshot}

    return on_snapshot


async def get_collection_data(collection_name):
    return {doc.id: doc.to_dict() for doc in
            getattr(admin_firestore_client, f'{collection_name}_client').collection.get()}


async def fill_initial_cache(q: Q):
    results = await asyncio.gather(*(get_collection_data(name) for name in LEAGUE_MANAGER_ITEMS_LIST))

    for collection_name, result in zip(LEAGUE_MANAGER_ITEMS_LIST, results):
        module_global_collection_cache[collection_name] = result

        setattr(q.app, f'{collection_name}_collection', result)
        setattr(q.app, f'{collection_name}_collection_subscriber', getattr(
            admin_firestore_client, f'{collection_name}_client').collection
                .on_snapshot(create_on_snapshot_callback(collection_name=collection_name)))


async def update_models(q: Q):
    await q.page.save()  # To preload the page

    if not module_global_collection_cache["initialized"] or not q.app.initialized:
        print("Initializing the Model Caches for Application, this may take a few seconds...")
        module_global_collection_cache["initialized"] = True
        q.app.initialized = True
        await q.run(fill_initial_cache, q)
        print("Finished Initializing the Model Caches for Application")

    for collection_name in LEAGUE_MANAGER_ITEMS_LIST:
        setattr(q.app, f'{collection_name}_collection', module_global_collection_cache[collection_name])
    q.app.collections_last_updated = datetime.datetime.now()


async def load_page_recipe_with_update_models(q: Q, page_callback_function):
    await page_callback_function(q)
    await q.page.save()
    return await asyncio.gather(page_callback_function(q), update_models(q))
