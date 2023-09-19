import inspect
from typing import List

from firebase_admin import firestore
from h2o_wave import Q, ui, on, data, handle_on, AsyncSite  # noqa F401

from src.BaseClasses.BaseClasses import FirestoreIDType
from src.BaseClasses.RulesBaseClasses import BaseRules
from src.ServerSideFrontendWave.firestore_update_models import load_page_recipe_with_update_models
from src.ServerSideFrontendWave.util import clear_cards, add_card, push_notification_bar
from src.ServerSideFrontendWave.util import load_env_file
from src._mappings import ITEM_NAME_TO_PYDANTIC_MODEL_MAP, \
    ITEM_NAME_TO_COLLECTION_NAME_MAPPING, LEAGUE_MANAGER_ITEM_NAME_LIST

load_env_file("/home/ruben/PycharmProjects/LeaguesManager/.env")

db = firestore.client()
from src.ServerSideFrontendWave.AdminFirestoreOperations import AdminFirestoreClient

admin_firestore_client = AdminFirestoreClient(db)
app = AsyncSite()

###!!!
_idfoo = 0


class Issue:
    def __init__(self, text: str, status: str, progress: float, icon: str, state: str, created: str):
        global _idfoo
        _idfoo += 1
        self.id = f'I{_idfoo}'
        self.text = text
        self.status = status
        self.views = 0
        self.progress = progress
        self.icon = icon
        self.created = created
        self.state = state


###!!!

async def leagues_management_page(q: Q):
    # Clear all cards except the ones needed for this page
    await q.run(clear_cards, q, ignore=['Application_Sidebar'])

    '''Context - Data from Firestore'''
    print(f'{q.app.sports_collection = }')
    '''Static Cards'''
    # Add header
    add_card(q, 'ALM_Header', ui.header_card(box='header', title='Leagues Management', subtitle='Admin',
                                             # Color
                                             color='transparent',
                                             icon='MoreSports',
                                             icon_color=None,
                                             ))
    # Add header right
    add_card(q, 'ALM_Commands', ui.form_card(
        box='first_context_1',
        items=[
            ui.button(name='ALM_commands_button', label='Commands', commands=[
                ui.command(name='ALM_new_item_command', label='New Item', items=[
                    ui.command(name='ALM_new_sport', label='Sport'),
                    ui.command(name='ALM_new_league', label='League'),
                    ui.command(name='ALM_new_season', label='Season'),
                    ui.command(name='ALM_new_team', label='Team'),
                ]),
                ui.command(name='ALM_edit_item_command', label='Edit Item', items=[
                    ui.command(name='ALM_edit_copy_button', label='Start from an Item'),
                    ui.command(name='ALM_edit_original_button', label='Edit Original Item'),
                ]),
                ui.command(name='ALM_erase_item_command', label='Delete Item', items=[
                    ui.command(name='ALM_archive_button', label='Archive Item'),
                    ui.command(name='ALM_delete_button',
                               label='ANNIHILATE THIS Item OUT of Existence!'),
                ])
            ]),

            # ui.button(name='ALM_edit_operation', label='Edit', primary=False),
            # ui.button(name='ALM_drop_operation', label='Drop', primary=False),
            # # Reload the page
            # ui.button(name='ALM_reload_operation', label='Reload', primary=False),

        ]
    ))
    '''Dynamic Cards'''
    #

    if q.args.issues:
        add_card(q, 'ALM_Main_Table',
                 ui.form_card(box='grid', items=[
                     ui.text(f'You clicked on: {q.args.issues}'),
                     ui.button(name='back', label='Back'),
                 ])
                 )
    else:
        print(f'{q.app.sports_collection.items() = }')
        # {'Soccer': {'status': 'inactive', 'name': 'Soccer'}, 'asfdewsd': {'status': 'inactive', 'name': 'asfdewsd'},
        #  'dfs': {'status': 'inactive', 'name': 'dfs'}, 'sfeds': {'status': 'inactive', 'name': 'sfeds'}}

        sports = [ui.table_row(
            name=sport_id,
            cells=[sport['name'], sport['status']]
        ) for sport_id, sport in q.app.sports_collection.items()]
        print(f'fhiseohf;W{sports = }')

        columns = [
            # (name: str,
            # label: str,
            # min_width: str | None = None,
            # max_width: str | None = None,
            # sortable: bool | None = None,
            # searchable: bool | None = None,
            # filterable: bool | None = None,
            # link: bool | None = None,
            # data_type: str | None = None,
            # cell_type: TableCellType | None = None,
            # cell_overflow: str | None = None,
            # filters: list[str] | None = None,
            # align: str | None = None)
            ui.table_column(name='name', label='Name', sortable=True, searchable=True, max_width='300',
                            cell_overflow='wrap'),
            ui.table_column(name='status', label='Status', filterable=True),

        ]

        add_card(q, 'ALM_Main_Table',
                 ui.form_card(box='grid', items=[
                     ui.table(
                         name='ALM_main_table_card',
                         columns=columns,
                         rows=sports,
                         groupable=True,
                         downloadable=True,
                         resettable=True,
                         height='600px'
                     )
                 ])
                 )


@on("ALM_new_item_command")
@on("ALM_new_sport")
@on("ALM_new_league")
@on("ALM_new_season")
@on("ALM_new_team")
async def on_ALM_new_item_command(q: Q):
    # Use LEAGUE_MANAGER_ITEM_NAME_LIST to check which is True ALM_new_{item_name} in q.args
    new_item_type = None
    for item in LEAGUE_MANAGER_ITEM_NAME_LIST:
        if q.args[f'ALM_new_{item}']:
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
        add_card(q, 'ALM_Commands',
                 ui.form_card(
                     box='first_context_1',
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
