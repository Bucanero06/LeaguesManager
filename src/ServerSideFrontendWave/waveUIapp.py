import asyncio

from h2o_wave import main, Q, app, ui, on, data, handle_on  # noqa F401

# FIXME DELETE VVVVVVV
from firebase_admin import firestore, credentials, initialize_app
cred = credentials.Certificate("...")
db = firestore.client(app=initialize_app(cred))
# FIXME DELETE ^^^^^^^


from src.ServerSideFrontendWave.wave_auth import initialize_client, render_hidden_content
from src.ServerSideFrontendWave.firestore_update_models import update_models


@on('global_notification_bar.dismissed')
async def on_global_notification_bar_dismissed(q: Q):
    # Delete the notification bar
    q.page['meta'].notification_bar = None
    await q.page.save()


@app('/')
async def serve(q: Q):
    """Main application handler."""
    print("Serving")
    if not q.client.initialized:
        print("Initializing")
        await initialize_client(q)
        if not q.app.initialized:
            await update_models(q)

        q.app.sports_collection = {}
        q.app.collections_last_updated = None
        q.app.leagues_collection = {}
        q.app.seasons_collection = {}
        q.app.games_collection = {}
        q.app.players_collection = {}
        q.app.teams_collection = {}
        q.app.clubs_collection = {}

    # return

    # await asyncio.gather(
    #     serve_security(q),
    #     q.run(update_models, q))
    # # FIXME DELETE VVVVVVV
    await asyncio.gather(
        render_hidden_content(q),
        q.run(update_models, q))
    # # FIXME DELETE ^^^^^^^

    await q.page.save()
    await handle_on(q)
