import asyncio

from h2o_wave import main, Q, app, ui, on, data, handle_on  # noqa F401

from src.ServerSideFrontendWave.util import clear_cards, add_card, stream_message


async def homepage(q: Q):
    print("Loading homepage")
    await q.run(clear_cards, q, ignore=['Application_Sidebar'])
    # q.page['sidebar'].value = '#homepage'

    for i in range(3):
        add_card(q, f'info{i}', ui.tall_info_card(box='horizontal', name='', title='Speed',
                                                  caption='The models are performant thanks to...', icon='SpeedHigh'))

    with open('static/ServicesPitchContent.md', 'r') as f:
        SERVICESPITCHCONTENT = f.read()
    add_card(q, 'article', ui.tall_article_preview_card(
        box=ui.box('vertical', height='600px'), title='How does magic work',
        image='https://avatars.githubusercontent.com/u/60953006?v=4',
        content=SERVICESPITCHCONTENT,
    ))

    add_card(
        q, 'AH_ChatBot', ui.chatbot_card(
            box='grid',
            data=data(fields='content from_user', t='list'),
            name='AH_chatbot_card',
            events=['stop'],
            placeholder='Ask me anything ...',
        )
    )

    # Add
    print(f'dsffesf{q.args = }')

    # Handle the stop event.
    if q.events.AH_chatbot_card and q.events.AH_chatbot_card.stop:
        # Cancel the streaming task.
        q.client.task.cancel()
        # Hide the "Stop generating" button.
        q.page['AH_ChatBot'].generating = False
    # A new message arrived.
    elif q.args.AH_chatbot_card:
        # Append user message.
        q.page['AH_ChatBot'].data += [q.args.AH_chatbot_card, True]
        # Run the streaming within cancelable asyncio task.
        q.client.task = asyncio.create_task(stream_message(q, 'AH_ChatBot',
                                                           message=f'You said: {q.client.AH_ChatBot_initialized}'))








