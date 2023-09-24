"""
A module for managing cache of Firestore collections and updating application models.

Module Dependencies
-------------------
- asyncio: Used for asynchronous function operations.
- datetime: Used to get the current datetime for cache updates.
- threading: Provides threading capabilities, particularly `Lock` for thread-safe operations.
- firestore: Firebase Firestore client.
- h2o_wave: Used for the Wave server front-end.
- AdminFirestoreClient: Custom client for managing Firestore operations.
- LEAGUE_MANAGER_ITEMS_LIST, ITEM_NAME_TO_COLLECTION_NAME_MAPPING, COLLECTION_NAME_TO_ITEM_NAME_MAPPING: Mappings for the Firestore collections.
- module_global_collection_cache: Global cache for holding collection data.

Global Variables
----------------
- cache_lock: Lock object used to ensure thread-safety when updating the global cache.
- db: Firestore client instance.
- admin_firestore_client: Instance of `AdminFirestoreClient` for managing Firestore operations.

Important Considerations
------------------------
1. **Concurrency**:
   - The module makes use of the `threading.Lock` object (`cache_lock`) to ensure that updates to the global cache (`module_global_collection_cache`) are thread-safe.
   - When working with the cache or making modifications, always ensure you acquire the lock to prevent potential data corruption or race conditions.

2. **Initialization**:
   - Upon starting the application, the cache is not initialized by default. The `update_models` function checks if initialization is required and then populates the cache.
   - Make sure to always invoke `update_models` before accessing data to ensure the cache is updated and initialized.

3. **Dependencies**:
   - The module depends heavily on Firebase Firestore. Ensure that Firestore is correctly set up and that the necessary credentials are available.
   - The `AdminFirestoreClient` should be appropriately configured to access and manage Firestore collections.

4. **Caching**:
   - The cache is a simple dictionary object (`module_global_collection_cache`). It is not persistent; restarting the application will reset the cache. If persistent caching is required, consider integrating with tools like Redis.
   - Data is cached for better performance and reduced Firestore calls. But be cautious about cache staleness. Regularly updating the cache or implementing cache expiration logic can be helpful.

5. **Data Mappings**:
   - The module uses several mappings (`LEAGUE_MANAGER_ITEMS_LIST`, `ITEM_NAME_TO_COLLECTION_NAME_MAPPING`, `COLLECTION_NAME_TO_ITEM_NAME_MAPPING`). Ensure they are correctly set up to match the Firestore collections.

Usage
-----
1. **Loading Data**:
   - To fetch and cache data, simply call the `load_page_recipe_with_update_models` function. This function takes care of updating models and then invoking the provided `page_callback_function`.

2. **Checking Cache Status**:
   - You can check if the cache has been initialized by examining the `module_global_collection_cache["initialized"]` value.

Maintenance & Troubleshooting
-----------------------------
1. **Logging**:
   - The module prints messages (e.g., initialization status). Consider integrating a robust logging framework for better visibility and troubleshooting in production environments.

2. **Error Handling**:
   - This module does not contain explicit error handling. Depending on the usage scenario, consider adding try-catch blocks, especially around Firestore interactions.

3. **Updates & Modifications**:
   - If additional Firestore collections are introduced, update the relevant mappings (`LEAGUE_MANAGER_ITEMS_LIST`, etc.) and the functions to accommodate them.
"""
import asyncio
import datetime
import threading

from firebase_admin import firestore
from h2o_wave import Q

from src.ServerSideFrontendWave.AdminFirestoreOperations import AdminFirestoreClient
from src._mappings import LEAGUE_MANAGER_ITEMS_LIST
from src.ServerSideFrontendWave._globals import module_global_collection_cache

cache_lock = threading.Lock()

try:
    db = firestore.client()
except Exception as e:
    from firebase_admin import firestore, credentials, initialize_app

    print(f'Error initializing Firestore client: {e}, retrying using credentials file...')
    cred = credentials.Certificate("onlythemotivated-c2c2e-b5f9ea606b36.json")
    db = firestore.client(app=initialize_app(cred))

admin_firestore_client = AdminFirestoreClient(db)


def create_on_snapshot_callback(collection_name: str):
    """
    Creates a callback for Firestore on_snapshot events.

    :param collection_name: Name of the Firestore collection.
    :return: Callback function to handle snapshot events.
    """

    def on_snapshot(doc_snapshot, changes, read_time):
        with cache_lock:
            print(f'{doc_snapshot = }')
            module_global_collection_cache[collection_name] = {doc.id: doc.to_dict() for doc in doc_snapshot}

    return on_snapshot


async def get_last_updated_collection_data(collection_name):
    """
    Asynchronously fetches data from a Firestore collection.

    :param collection_name: Name of the Firestore collection.
    :return: Dictionary containing document IDs as keys and their corresponding data as values.
    """
    return {doc.id: doc.to_dict() for doc in
            getattr(admin_firestore_client, f'{collection_name}_client').collection.get(

            )}


async def fill_initial_cache(q: Q):
    """
    Fills the initial cache with Firestore collection data.

    :param q: Wave server Q object.
    :return: None.
    """
    results = await asyncio.gather(*(get_last_updated_collection_data(name) for name in LEAGUE_MANAGER_ITEMS_LIST))

    for collection_name, result in zip(LEAGUE_MANAGER_ITEMS_LIST, results):
        module_global_collection_cache[collection_name] = result

        setattr(q.app, f'{collection_name}_collection', result)
        setattr(q.app, f'{collection_name}_collection_subscriber', getattr(
            admin_firestore_client, f'{collection_name}_client').collection
                .on_snapshot(create_on_snapshot_callback(collection_name=collection_name)))


async def update_models(q: Q):
    """
    Updates the application models with the latest data from the Firestore collections.

    :param q: Wave server Q object.
    :return: None.
    """
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
    """
    Loads a page after updating the application models.

    :param q: Wave server Q object.
    :param page_callback_function: Callback function for page loading.
    :return: Result of the `page_callback_function` and `update_models` functions.

    """
    await page_callback_function(q)
    await q.page.save()
    return await asyncio.gather(page_callback_function(q), update_models(q))
