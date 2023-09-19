import json
import os

import requests
from h2o_wave import Q, app, ui, on, data, handle_on, AsyncSite  # noqa F401

from src.ServerSideFrontendWave.Pages.AdminPages.AdminAccountPage import admin_account_page
from src.ServerSideFrontendWave.Pages.AdminPages.AdminFinancials import admin_stripe_page
from src.ServerSideFrontendWave.Pages.AdminPages.AdminHomePage import homepage
from src.ServerSideFrontendWave.Pages.AdminPages.AdminLeaguesManagementPage import leagues_management_page
from src.ServerSideFrontendWave.Pages.AdminPages.AdminPlansPage import admin_plans_page
from src.ServerSideFrontendWave.firestore_update_models import load_page_recipe_with_update_models
from src.ServerSideFrontendWave.util import clear_cards, add_card, load_env_file

load_env_file("/home/ruben/PycharmProjects/LeaguesManager/.env")
FIREBASE_CONFIG = {
    "apiKey": os.environ.get("FIREBASE_API_KEY"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.environ.get("FIREBASE_APP_ID"),
    "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID"),

}


# FIXME UNCOMMENT VVVVVVV
# cred = credentials.Certificate("onlythemotivated-c2c2e-b5f9ea606b36.json")
# db = firestore.client(app=firebase_admin.initialize_app(cred))
# FIXME UNCOMMENT ^^^^^^^


async def init(q: Q) -> None:
    """
    Q Page Meta (meta_card) Arguments:
        box
            A string indicating how to place this component on the page.
        title
            The title of the page.
        refresh
            Refresh rate in seconds. A value of 0 turns off live-updates. Values != 0 are currently ignored (reserved for future use).
        notification
            Display a desktop notification.
        notification_bar
            Display an in-app notification bar.
        redirect
            Redirect the page to a new URL.
        icon
            Shortcut icon path. Preferably a .png file (.ico files may not work in mobile browsers). Not supported in Safari.
        layouts
            The layouts supported by this page.
        dialog
            Display a dialog on the page.
        side_panel
            Display a side panel on the page.
        theme
            Specify the name of the theme (color scheme) to use on this page. One of 'light', 'neon' or 'h2o-dark'.
        themes
            Themes (color schemes) that define color used in the app.
        tracker
            Configure a tracker for the page (for web analytics).
        scripts
            External Javascript files to load into the page.
        script
            Javascript code to execute on this page.
        stylesheet
            CSS stylesheet to be applied to this page.
        stylesheets
            External CSS files to load into the page.
        commands
            Contextual menu commands for this component.
    """
    # Static Business Website
    # index_file = open('static/html/index.html', 'r').read()

    q.page['meta'] = ui.meta_card(box='',
                                  title='8CoedSports',
                                  layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
                                      ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
                                          ui.zone('sidebar', size='208px'),
                                          ui.zone('body', zones=[
                                              ui.zone('header'),
                                              ui.zone('content', zones=[
                                                  # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                                                  ui.zone('first_context', size='0 0 1 4',
                                                          direction=ui.ZoneDirection.ROW,
                                                          zones=[
                                                              ui.zone('first_context_1', size='1 4 0 0'),
                                                              ui.zone('first_context_2', size='1 4 0 0'),
                                                              ui.zone('first_context_3', size='1 4 0 0'),
                                                              ui.zone('first_context_3', size='1 4 0 0'),
                                                          ]),
                                                  ui.zone('second_context', size='0 0 1 4',
                                                          direction=ui.ZoneDirection.ROW,
                                                          zones=[
                                                              ui.zone('second_context_1', size='1 4 0 0'),
                                                              ui.zone('second_context_2', size='1 4 0 0'),
                                                              ui.zone('second_context_3', size='1 4 0 0',
                                                                      direction=ui.ZoneDirection.ROW,
                                                                      zones=[
                                                                          ui.zone('second_context_3_1', size='1 4 0 0'),
                                                                          ui.zone('second_context_3_2', size='1 4 0 0')
                                                                      ]),
                                                          ]),
                                                  ui.zone('details', size='4 4 4 4'),
                                                  ui.zone('horizontal', size='1', direction=ui.ZoneDirection.ROW),
                                                  ui.zone('centered', size='1 1 1 1', align='center'),
                                                  ui.zone('vertical', size='1'),
                                                  ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch',
                                                          justify='center'),

                                              ]),
                                          ]),
                                      ]),
                                      ui.zone('footer', size='0 1 0 0', direction=ui.ZoneDirection.ROW),
                                  ]),
                                           ],
                                  themes=[
                                      ui.theme(
                                          name='my-awesome-theme',
                                          primary='#8C1B11',  # Header and Sidebaer - Color Light Red
                                          text='#000000',  #
                                          card='#ffffff',
                                          page='#F2F2F2',
                                          # page='#D91A1A',

                                      )
                                  ],
                                  theme='my-awesome-theme'

                                  )
    # Sidebar should be initialized only with non-authenticated pages content only!!!
    add_card(q, 'Application_Sidebar', ui.nav_card(
        box='sidebar', color='primary', title='Demo Admin App',
        subtitle="The team sports you loved as a kid... now all grown up.",
        # Local Image
        image='https://8coedsports.com/wp-content/uploads/2019/12/8coed-logo-color.svg',
        items=[]
    ))
    q.page['footer'] = ui.footer_card(box='footer',
                                      caption='©2023 8CoedSports & Carbonyl LLC. Partnership. All rights reserved.')

    q.client.initialized = False


async def initialize_client(q: Q):
    q.client.cards = set()
    await init(q)
    q.client.initialized = True
    q.client.token = None  # Initially, no token is set.


def authenticate_with_firebase(email, password):
    """Authenticate with Firebase and return token if successful, or an error message."""
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}"
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        response = requests.post(endpoint, data=json.dumps(data))
        response_data = response.json()

        if "idToken" in response_data:
            return {
                'status': 'success',
                'error_message': None,
                'token': response_data.get('idToken'),
                'refresh_token': response_data.get('refreshToken'),
                'user_id': response_data.get('localId'),
                'email': response_data.get('email'),
                'expires_in': response_data.get('expiresIn'),
            }

        elif "error" in response_data:
            return {
                'status': 'error',
                'error_message': f"Authentication failed: {response_data['error'].get('message', 'Unknown error.')}",
                'token': None,
                'refresh_token': None,
                'user_id': None,
                'email': None,
                'expires_in': None,
            }
    except requests.RequestException as e:
        return {
            'status': 'error',
            'error_message': f"Authentication failed: {e}",
            'token': None,
            'refresh_token': None,
            'user_id': None,
            'email': None,
            'expires_in': None,
        }
    return {
        'status': 'error',
        'error_message': f"Authentication failed: Unknown error.",
        'token': None,
        'refresh_token': None,
        'user_id': None,
        'email': None,
        'expires_in': None,
    }


def check_token_validity(idToken):
    """Check if a Firebase token is valid."""
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_CONFIG['apiKey']}"
    data = {"idToken": idToken}
    response = requests.post(endpoint, data=json.dumps(data))
    return (response.status_code == 200)


async def render_login_page(q: Q, error_message=None):
    """Render the login page."""

    clear_cards(q)

    await init(q)

    items = [
        ui.text_xl('Login'),
        ui.textbox(name='email', label='Email', required=True),
        ui.textbox(name='password', label='Password', required=True, password=True),
        ui.buttons([ui.button(name='login', label='Login', primary=True, )]),
    ]
    if error_message:
        items.insert(0, ui.message_bar(type='error', text=error_message, ))

    add_card(q, 'login', ui.form_card(box='centered', items=items, ), )


async def render_hidden_content(q: Q, context: dict = None):
    """
    Render pages content e.g. homepage or other pages get added here
    """

    # First clear all cards
    await q.run(clear_cards, q, ignore=['Application_Sidebar'])

    # Then add the sidebar
    add_card(q, 'Application_Sidebar', ui.nav_card(
        box='sidebar', color='primary', title='LeagueApp',
        subtitle="The team sports you loved as a kid... now all grown up.",
        value=f'#{q.args["#"]}' if q.args['#'] else '#homepage',
        # image='https://wave.h2o.ai/img/h2o-logo.svg', items=[]
        # Loading from local file rather than url
        image='https://8coedsports.com/wp-content/uploads/2019/12/8coed-logo-color.svg', items=[
            ui.nav_group('Main', items=[
                ui.nav_item(name='#homepage', label='Home', icon='Home'),
                ui.nav_item(name='#admin_stripe_page', label='Admin Stripe', icon='FinancialMirroredSolid'),
                ui.nav_item(name='#leagues_management_page', label='Leagues Management', icon='MoreSports'),
            ]),
            ui.nav_group('Account', items=[
                ui.nav_item(name='#admin_account_page', label='Account', icon='AccountManagement'),
                ui.nav_item(name='#admin_plans_page', label='Plans', icon='PaymentCard'),
                ui.nav_item(name='logout', label='Logout', icon='Logout'),
            ]),
        ],
    ))

    if q.args['#'] == 'homepage':
        await load_page_recipe_with_update_models(q, homepage)
    elif q.args['#'] == 'admin_stripe_page':
        await load_page_recipe_with_update_models(q, admin_stripe_page)
    elif q.args["#"] == "admin_account_page":
        await load_page_recipe_with_update_models(q, admin_account_page)
    elif q.args["#"] == "admin_plans_page":
        await load_page_recipe_with_update_models(q, admin_plans_page)
    elif q.args["#"] == 'leagues_management_page':
        await load_page_recipe_with_update_models(q, leagues_management_page)


async def serve_security(q: Q):
    response = None
    # If logout is triggered, clear token and show login page
    if q.args.logout:
        q.client.token = None
        await render_login_page(q)
        return  # End the function after logging out

    # If login is triggered, try to authenticate and decide what to render next
    if q.args.login:
        response = authenticate_with_firebase(q.args.email, q.args.password)

        if response['status'] == 'success':
            print("Token already exists and is valid")
            q.client.token = response['token']
            await render_login_page(q, error_message=response['error_message'])
        else:
            await render_login_page(q, error_message=response['error_message'])
            return  # End the function if login fails

    # If the client already has a token, check its validity and act accordingly
    if q.client.token:
        if check_token_validity(q.client.token):
            context = response  # todo: implement better context handling
            await render_hidden_content(q, context)
        else:
            q.client.token = None
            await render_login_page(q)
    else:
        await render_login_page(q)
