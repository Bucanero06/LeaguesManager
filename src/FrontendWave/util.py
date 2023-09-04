from h2o_wave import Q
from typing import Optional, List


def add_card(q: Q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


def clear_cards(q: Q, ignore: Optional[List[str]] = None) -> None:
    """
    Clear cards from the page except those listed in 'ignore'.
    """
    print("Clearing cards")

    if not ignore:
        ignore = []

    # If no cards are present, simply return
    if not hasattr(q.client, 'cards') or not q.client.cards:
        print("No cards")
        return

    # Remove cards not in the ignore list
    for card_name in q.client.cards.copy():
        if card_name not in ignore:
            del q.page[card_name]
            q.client.cards.remove(card_name)
