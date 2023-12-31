import os

import firebase_admin
from firebase_admin import credentials, firestore
from h2o_wave import  Q, app, ui, on, data  # noqa F401
from src.ServerSideFrontendWave.util import clear_cards, add_card, dynamic_tall_series_stat_card
from src.ServerSideFrontendWave.util import load_env_file
from src.BaseClasses.FirestoreClient import AsyncPydanticFirestoreClient


load_env_file("/home/ruben/PycharmProjects/LeaguesManager/.env")

import stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")





async def admin_stripe_page(q: Q):
    await q.run(clear_cards, q, ignore=['Application_Sidebar'])

    '''Static Cards'''
    # Add header
    add_card(q, 'header_card', ui.header_card(box='header', title='Association Finances', subtitle='Admin',
                                              # Color
                                              color='transparent',
                                              icon='PaymentCard',
                                              icon_color=None,
                                              ))
    # TODO: Per Page store a list of widgets to update, this should transition to a database call

    '''Dynamic Cards'''
    # Overview Cards

    # Remove dynamic_card from widget_dict

    admin_stripe_balance_message = stripe.Balance.retrieve()

    available = admin_stripe_balance_message['available'][0]
    pending = admin_stripe_balance_message['pending'][0]

    available_amount = available['amount']
    available_currency = available['currency']
    available_card = available['source_types']['card']

    pending_amount = pending['amount']
    pending_currency = pending['currency']
    pending_card = pending['source_types']['card']

    add_card(q, 'first_context_1', ui.stat_list_card(
        box='first_context_1',
        title='Available Balance',
        items=[
            ui.stat_list_item(label='Amount', value=f'{available_currency} {available_amount/100}'),  # Divided by 100 to convert to dollars
            ui.stat_list_item(label='Currency', value=available_currency),
            ui.stat_list_item(label='Card', value=f'{available_currency} {available_card/100}'),
        ]
    ))
    add_card(q, 'first_context_2', ui.stat_list_card(
        box='first_context_2',
        title='Pending Balance',
        items=[
            ui.stat_list_item(label='Amount', value=f'{pending_currency} {pending_amount/100}'),  # Divided by 100 to convert to dollars
            ui.stat_list_item(label='Currency', value=pending_currency),
            ui.stat_list_item(label='Card', value=f'{pending_currency} {pending_card/100}'),
        ]
    ))



    print(f'admin_stripe_balance_message: {admin_stripe_balance_message}')

    add_card(q, 'first_context_3', dynamic_tall_series_stat_card(
        box='first_context_3',
        title='Revenue',
        main_stat=43,  # For example, dynamically fetch this value
        aux_stat=0.85,
        chart_data=data('foo qux', 3, rows=[[85, 0.5], [60, 0.6], [85, 0.85]]),
        additional_params={
            'plot_type': 'area',
            'plot_category': 'foo',
            'plot_value': 'qux',
            'plot_color': '$blue',
            'plot_curve': 'linear',
        }

    ))

    # # To stop listening
    # collection_watch.unsubscribe()

    add_card(q, 'AS_Time_Range_Period', ui.form_card(
        box='first_context_4',
        items=[
            ui.dropdown(
                # def dropdown(name: str, label: Optional[str] = None, placeholder: Optional[str] = None, value: Optional[str] = None, values: Optional[List[str]] = None, choices: Optional[List[Choice]] = None, required: Optional[bool] = None, disabled: Optional[bool] = None, trigger: Optional[bool] = None, width: Optional[str] = None, visible: Optional[bool] = None, tooltip: Optional[str] = None, popup: Optional[str] = None) ‑> Component
                name='Last Month',
                choices=[
                    ui.choice(name='AS_range_month_to_date_choice', label='Month-to-Date'),
                    ui.choice(name='AS_range_quarter_to_date_choice', label='Quarter-to-Date'),
                    ui.choice(name='AS_range_year_to_date_choice', label='Year-to-Date'),
                ],
                placeholder= 'Last Month',
            )
        ]
    )

    )

@on('AS_range_month_to_date_choice')
async def AS_range_month_to_date_choice(q: Q):
    await q.page.save()
    await admin_stripe_page(q)
