from h2o_wave import main, Q, app, ui, on, data, handle_on  # noqa F401

from src.ServerSideFrontendWave.util import clear_cards, add_card



async def homepage(q: Q):
    print("Loading homepage")
    clear_cards(q)
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








