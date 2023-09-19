"""This Page is where the Admin/Business-Owner/Partner can interact with the service provider and the system to manage their
    association with Carbonyl, also personal information."""
import os

import firebase_admin
from firebase_admin import credentials, firestore
from h2o_wave import Q, app, ui, on, data, handle_on  # noqa F401

from src.BaseClasses.FirestoreClient import AsyncPydanticFirestoreClient
from src.ServerSideFrontendWave.util import clear_cards, add_card, dynamic_tall_series_stat_card
from src.ServerSideFrontendWave.util import load_env_file

load_env_file("/home/ruben/PycharmProjects/LeaguesManager/.env")

import stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")


async def admin_account_page(q: Q):
    """
    [dict(
            card_id={{firestore_id}},
            box_name={{(box/zone)_name}},
            dynamic_card={{dynamic_card_function}}, # Custom
        ), ... ]
    """
    await q.run(clear_cards, q, ignore=['Application_Sidebar'])

    '''Static Cards'''
    # Add header
    add_card(q, 'header_card', ui.header_card(box='header', title='Association Account', subtitle='Admin',
                                              # Color
                                              color='transparent',
                                              icon='AccountManagement',
                                              icon_color=None,
                                              ))