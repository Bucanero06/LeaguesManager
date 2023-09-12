import asyncio
import inspect
from typing import List

from firebase_admin import firestore
from h2o_wave import Q, ui, on, data, handle_on, AsyncSite  # noqa F401

from src.BaseClasses.BaseClasses import FirestoreIDType
from src.BaseClasses.RulesBaseClasses import BaseRules
from src.ServerSideFrontendWave.Pages.AdminPages._mappings import ITEM_NAME_TO_PYDANTIC_MODEL_MAP, \
    ITEM_NAME_TO_COLLECTION_NAME_MAPPING, LEAGUE_MANAGER_ITEM_NAME_LIST
from src.ServerSideFrontendWave.firestore_update_models import load_page_recipe_with_update_models
from src.ServerSideFrontendWave.util import clear_cards, add_card, push_notification_bar, stream_message
from src.ServerSideFrontendWave.util import load_env_file

load_env_file("/home/ruben/PycharmProjects/LeaguesManager/.env")

db = firestore.client()
from src.ServerSideFrontendWave.AdminFirestoreOperations import AdminFirestoreClient

admin_firestore_client = AdminFirestoreClient(db)
app = AsyncSite()


async def leagues_management_page(q: Q):
    # Clear all cards except the ones needed for this page
    clear_cards(q,
                # Optional[List[str]] # TODO change to page object naming convension e.g. {A (Admin) or U (User)}{PageName Initials}
                ignore=['header_card', 'SportsLeaguesDropdowns', 'SeasonsDropdowns', 'CRUDOperations',
                        "ALM_ChatBot_Area","first_context_1"]
                )

    '''Context - Data from Firestore'''

    '''Static Cards'''
    # Add header
    add_card(q, 'header_card', ui.header_card(box='header', title='Leagues Management', subtitle='Admin',
                                              # Color
                                              color='transparent',
                                              icon='MoreSports',
                                              icon_color=None,
                                              ))

    '''Dynamic Cards'''
    sports_choices = [ui.choice(name=sport_id, label=sport_id) for sport_id in
                      q.app.sports_collection.keys()] if q.app.sports_collection else []
    leagues_available_with_sport = [ui.choice(name=league_id, label=league_id) for league_id in  # TODO
                                    q.app.leagues_collection.keys()] if q.app.leagues_collection else []
    seasons_available_with_league = [ui.choice(name=season_id, label=season_id) for season_id in
                                     q.app.seasons_collection.keys()] if q.app.seasons_collection else []
    teams_available_with_season = [ui.choice(name=team_id, label=team_id) for team_id in
                                   q.app.teams_collection.keys()] if q.app.teams_collection else []

    # League Management Cards
    add_card(q, 'CRUDOperations',
             # Select league if not any created then create, if sport not created then create, etc...
             ui.form_card(
                 box='first_context_1',
                 items=[
                     ui.button(name='ALM_manual_commands_button', label='Manual Admin Commands', commands=[
                         ui.command(name='ALM_manual_new_command', label='Add a New Item', items=[
                             ui.command(name='ALM_manual_new_sport', label='Sport'),
                             ui.command(name='ALM_manual_new_league', label='League'),
                             ui.command(name='ALM_manual_new_season', label='Season'),
                             ui.command(name='ALM_manual_new_team', label='Team'),
                         ]),
                         ui.command(name='ALM_manual_edit_command', label='Edit Items', items=[
                             ui.command(name='ALM_manual_edit_copy_button', label='Start from an Item'),
                             ui.command(name='ALM_manual_edit_original_button', label='Edit Original Item'),
                         ]),
                         ui.command(name='ALM_manual_erase_command', label='Other commands', items=[
                             ui.command(name='ALM_manual_archive_button', label='Archive Item'),
                             ui.command(name='ALM_manual_delete_button',
                                        label='ANNIHILATE THIS Item OUT of Existence!'),
                         ])
                     ]),

                     # ui.button(name='ALM_edit_operation', label='Edit', primary=False),
                     # ui.button(name='ALM_drop_operation', label='Drop', primary=False),
                     # # Reload the page
                     # ui.button(name='ALM_reload_operation', label='Reload', primary=False),

                 ]
             )
             )

    add_card(q, 'SportsLeaguesDropdowns',
             # Select league if not any created then create, if sport not created then create, etc...
             ui.form_card(
                 box='first_context_1',
                 items=[
                     ui.dropdown(name='sport', label='Start with a Sport', choices=sports_choices),
                     ui.dropdown(name='league', label='These contain Leagues', choices=leagues_available_with_sport)
                 ],

             )
             )

    add_card(q, 'SeasonsDropdowns',
             # Select league if not any created then create, if sport not created then create, etc...
             ui.form_card(
                 box='first_context_1',
                 items=[
                     ui.dropdown(name='seasons', label='Choose Seasons', choices=seasons_available_with_league),
                     ui.dropdown(name='teams', label='Want to see Teams?', choices=teams_available_with_season),
                 ]
             )
             )

    add_card(
        q, 'AML_ChatBot_Area', ui.chatbot_card(
        box='first_context_1',
        data=data(fields='content from_user', t='list'),
        name='chatbot',
        events=['stop']
    )
    )

    print(f'dsffesf{q.args = }')


    # Handle the stop event.
    if q.events.chatbot and q.events.chatbot.stop:
        # Cancel the streaming task.
        q.client.task.cancel()
        # Hide the "Stop generating" button.
        q.page['AML_ChatBot_Area'].generating = False
    # A new message arrived.
    elif q.args.chatbot:
        # Append user message.
        q.page['AML_ChatBot_Area'].data += [q.args.chatbot, True]
        # Run the streaming within cancelable asyncio task.
        q.client.task = asyncio.create_task(stream_message(q, 'AML_ChatBot_Area',
                                                           message=f'You said: {q.client.AML_ChatBot_Area_initialized}'))





@on("ALM_manual_new_command")
@on("ALM_manual_new_sport")
@on("ALM_manual_new_league")
@on("ALM_manual_new_season")
@on("ALM_manual_new_team")
async def on_ALM_manual_new_command(q: Q):
    # Use LEAGUE_MANAGER_ITEM_NAME_LIST to check which is True ALM_manual_new_{item_name} in q.args
    for item in LEAGUE_MANAGER_ITEM_NAME_LIST:
        if q.args[f'ALM_manual_new_{item}']:
            new_item_type = item
            break

    q.client['#leagues_management_page.new_item_type'] = None
    if new_item_type:
        # Get Fields for the Pydanctic Model
        model_fields = ITEM_NAME_TO_PYDANTIC_MODEL_MAP[new_item_type].model_fields
        q.client['#leagues_management_page.new_item_type'] = new_item_type

        # Create the UI items for the form
        model_fields_ui_items = []
        for field_name, field_info in model_fields.items():
            # Check if the field is not hidden from schema extra and add it to the form
            if not (
                    hasattr(field_info.json_schema_extra, 'get') and field_info.json_schema_extra.get("hidden", False)
            ):

                # if field_info.annotation == FirestoreIDType:
                if inspect.isclass(field_info.annotation):
                    if issubclass(field_info.annotation, FirestoreIDType):
                        # If the field is required then dropdown is of currently ava

                        # split {item_name}_id
                        collection_name = ITEM_NAME_TO_COLLECTION_NAME_MAPPING[field_name.split('_id')[0]]

                        choices = [ui.choice(name=field_id, label=field_id) for field_id in
                                   getattr(q.app, f'{collection_name}_collection').keys()]
                        model_fields_ui_items.append(
                            ui.dropdown(name=field_name, label=field_name, choices=choices,
                                        required=field_info.is_required()))
                    elif inspect.isclass(field_info.annotation) and \
                            issubclass(field_info.annotation, BaseRules):

                        # Do a json like object editing ui for the rules
                        # model_fields_ui_items.append(
                        pass
                    else:
                        model_fields_ui_items.append(
                            ui.textbox(name=field_name, label=field_name, required=field_info.is_required()))

                elif field_info.annotation == List[FirestoreIDType]:
                    # TODO: This will be a multi-select dropdown if customizable but for now will only allow user to
                    #   adjust/edit when using the table
                    pass

                else:
                    model_fields_ui_items.append(
                        ui.textbox(name=field_name, label=field_name, required=field_info.is_required()))

        # Create wave form for user to fill in the fields
        add_card(q, 'CRUDOperations',
                 ui.form_card(
                     box='first_context_3',
                     items=[
                               # Title of the form
                               ui.text_xl(f'Create New {new_item_type.capitalize()}'),
                           ] + model_fields_ui_items + [
                               ui.button(name="ALM_create_new_document_on_db",
                                         label='Create', primary=True),
                               ui.button(name='ALM_back_to_operations',
                                         label='Back', primary=True),
                           ]
                 )
                 )

    else:
        # Create a notification bar
        await push_notification_bar(q, f"Please select an item type, no new item created",
                                    type='warning', timeout=5,
                                    buttons=None, position='top-right',
                                    events=['dismissed'], name="global_notification_bar")

    await q.page.save()




@on("ALM_back_to_operations")
async def ALM_back_to_operations(q: Q):
    # Set any used attributes to Default
    q.client['#leagues_management_page.new_item_type'] = None
    return await load_page_recipe_with_update_models(q, leagues_management_page)


@on("ALM_create_new_document_on_db")
async def ALM_create_new_document_on_db(q: Q):
    new_item_type = q.client['#leagues_management_page.new_item_type']

    pydantic_model_class = ITEM_NAME_TO_PYDANTIC_MODEL_MAP[new_item_type]

    model_fields = pydantic_model_class.model_fields
    #
    model_fields_ui_items = [
        field_name for field_name, field_info in model_fields.items()
        if not (hasattr(field_info.json_schema_extra, 'get') and field_info.json_schema_extra.get("hidden", False))
    ]
    #
    items_dict = {
        field_name: q.args[field_name] for field_name in model_fields_ui_items if field_name in q.args
    }
    print(f'{items_dict = }')
    print(f'{pydantic_model_class = }')
    print(f'{pydantic_model_class(**items_dict) = }')
    filled_model = await getattr(
        admin_firestore_client, f'{ITEM_NAME_TO_COLLECTION_NAME_MAPPING[new_item_type]}_client').create(
        pydantic_model_class(**items_dict))
    #
    await push_notification_bar(q, f"New {new_item_type.capitalize()} {filled_model.name} created successfully",
                                type='success', timeout=5,
                                buttons=None, position='top-right',
                                events=['dismissed'], name="global_notification_bar")

    q.client['#leagues_management_page.new_item_type'] = None
    #
    await q.page.save()
