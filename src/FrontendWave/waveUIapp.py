import json

import firebase_admin
import requests
from firebase_admin import credentials, firestore, auth
from h2o_wave import main, Q, app, ui, on, data, handle_on  # noqa F401

from src.FrontendWave.util import add_card, clear_cards
from src.FrontendWave.wave_auth import FIREBASE_CONFIG

# LEAGUESLOGO = 'https://8coedsports.com/wp-content/uploads/2019/12/8coed-logo-color.svg'
LEAGUESLOGO = 'https://avatars.githubusercontent.com/u/60953006?v=4'

print("Initializing firestore client")
cred = credentials.Certificate("onlythemotivated-c2c2e-b5f9ea606b36.json")
db = firestore.client(app=firebase_admin.initialize_app(cred))


@on('#homepage')
async def homepage(q: Q):
    clear_cards(q)
    print("Loading homepage")
    q.page['sidebar'].value = '#homepage'

    for i in range(3):
        add_card(q, f'info{i}', ui.tall_info_card(box='horizontal', name='', title='Speed',
                                                  caption='The models are performant thanks to...', icon='SpeedHigh'))

    with open('static/ServicesPitchContent.md', 'r') as f:
        SERVICESPITCHCONTENT = f.read()
    add_card(q, 'article', ui.tall_article_preview_card(
        box=ui.box('vertical', height='600px'), title='How does magic work',
        image=LEAGUESLOGO,
        content=SERVICESPITCHCONTENT,
        # Read the md file

        # SERVICESPITCHCONTENT
    ))


async def init(q: Q) -> None:

    q.page['meta'] = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
        ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
            ui.zone('sidebar', size='250px'),
            ui.zone('body', zones=[
                ui.zone('header'),
                ui.zone('content', zones=[
                    # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                    ui.zone('horizontal', size='1', direction=ui.ZoneDirection.ROW),
                    ui.zone('centered', size='1 1 1 1', align='center'),
                    ui.zone('vertical', size='1'),
                    ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                ]),
            ]),
        ])
    ])],
                                  )
    q.page['sidebar'] = ui.nav_card(
        box='sidebar', color='primary', title='LeagueApp',
        subtitle="The team sports you loved as a kid... now all grown up.",
        value=f'#{q.args["#"]}' if q.args['#'] else '#homepage',
        # image='https://wave.h2o.ai/img/h2o-logo.svg', items=[]
        # Loading from local file rather than url
        image=LEAGUESLOGO, items=[],

    )
    q.page['header'] = ui.header_card(
        box='header', title='', subtitle='',
    )
    # If no active hash present, render homepage.
    if q.args['#'] is None:
        await homepage(q)


async def initialize_client(q: Q):
    q.client.cards = set()
    await init(q)
    q.client.initialized = True
    q.client.token = None  # Initially, no token is set.


async def render_hidden_content(q: Q):
    # Render pages content e.g. homepage or other pages get added here
    if q.args['#'] == '#homepage':
        await homepage(q)
    else:
        await homepage(q)


async def render_login_page(q: Q, error_message=None):
    clear_cards(q)
    items = [
        ui.textbox(name='email', label='Email'),
        ui.textbox(name='password', label='Password', password=True),
        ui.buttons([ui.button(name='login', label='Login', primary=True)]),
    ]
    if error_message:
        items.insert(0, ui.text(error_message))
    q.page['login'] = ui.form_card(box='1 1 4 4', items=items)


# @app('/'))
# async def serve(q: Q):
#     if not q.client.initialized:
#         # Hack to define token for client
#         await initialize_client(q)
#
#     if q.client.token:
#         try:
#             # Verify the ID token sent from the client
#             decoded_token = auth.verify_id_token(q.client.token)
#             q.client.uid = decoded_token['uid']
#             await render_hidden_content(q)
#         except:
#             await render_login_page(q, error_message="Invalid session. Please log in again.")
#     else:
#         await render_login_page(q)


@app('/')
async def serve(q: Q):
    print("Serving")
    if not q.client.initialized:
        print("Initializing")
        await initialize_client(q)
        ...

    # Write hellow world
    q.page['hello'] = ui.form_card(box='1 1 4 4', items=[
        ui.textbox(name='name', label='Name', required=True),
        ui.button(name='submit', label='Submit', primary=True),
    ])

    await q.page.save()


    # if not q.client.token:
    #     await render_login_page(q)
    # else:
    #     if check_token_validity(q.client.token):
    #         await render_hidden_content(q)
    #     else:
    #         # Reset token
    #         q.client.token = None
    #         await render_login_page(q)
    #
    # if q.args.login:
    #     q.client.token = authenticate_with_firebase(q.args.email, q.args.password)
    #     if q.client.token:
    #         await render_hidden_content(q)
    #     else:
    #         await render_login_page(q, error_message="Invalid email or password. Please try again.")
    #
    # if q.args.logout:
    #     q.client.token = None
    #     await render_login_page(q)
    #
    # if q.args.token_received:
    #     q.client.token = q.args.token_received.token
    #     await render_hidden_content(q)
    #
    # if q.args['#'] == '#homepage':
    #     await homepage(q)
    # else:
    #     await homepage(q)
    #
    # await q.page.save()
