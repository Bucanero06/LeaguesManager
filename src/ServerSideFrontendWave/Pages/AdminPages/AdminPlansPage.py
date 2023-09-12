import os

from h2o_wave import Q, app, ui, on, data, handle_on  # noqa F401

from src.ServerSideFrontendWave.util import clear_cards, add_card
from src.ServerSideFrontendWave.util import load_env_file

load_env_file("/home/ruben/PycharmProjects/LeaguesManager/.env")

import stripe

stripe.api_key = os.getenv("STRIPE_API_KEY")


async def admin_plans_page(q: Q):
    clear_cards(q)

    '''Static Cards'''
    # Add header
    add_card(q, 'header_card', ui.header_card(box='header', title='Plans', subtitle='Admin',
                                              # Color
                                              color='transparent',
                                              icon='PaymentCard',
                                              icon_color=None,
                                              ))
