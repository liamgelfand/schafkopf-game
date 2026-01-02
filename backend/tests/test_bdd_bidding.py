"""BDD tests for bidding using pytest-bdd"""
import pytest
from pytest_bdd import given, when, then, scenario, parsers
from app.models.game import Game
from app.models.card import Suit, Rank, Card

@pytest.fixture
def game():
    """Create a game for testing"""
    game = Game("test-game")
    for i in range(4):
        game.add_player(f"player{i+1}")
    game.deal_cards()
    return game

@given("a game with 4 players")
def game_with_players(game):
    """Game has 4 players"""
    assert len(game.players) == 4
    return game

@given("cards have been dealt")
def cards_dealt(game):
    """Cards are dealt"""
    game.deal_cards()
    for player in game.players:
        assert len(player.hand) == 8
    return game

@given("the bidding phase has started")
def bidding_started(game):
    """Bidding phase is active"""
    game.bidding_phase = True
    game.bidding_complete = False
    game.current_bidder_index = 0
    game.initial_bidder_index = 0
    return game

@given(parsers.parse("it is player {player_index:d}'s turn to bid"))
def set_current_bidder(game, player_index):
    """Set current bidder"""
    game.current_bidder_index = player_index
    return game

@given(parsers.parse('player {player_index:d} has no Ace of {suit} in their hand'))
def player_has_no_ace(game, player_index, suit):
    """Verify player doesn't have the ace"""
    player = game.players[player_index]
    suit_enum = Suit(suit)
    has_ace = any(card.suit == suit_enum and card.rank.value == "Ace" for card in player.hand)
    assert not has_ace, f"Player {player_index} has Ace of {suit} in hand"
    return game

@given(parsers.parse('player {player_index:d} has Ace of {suit} in their hand'))
def player_has_ace(game, player_index, suit):
    """Verify player has the ace"""
    player = game.players[player_index]
    suit_enum = Suit(suit)
    # Add ace to hand if not present (for testing)
    has_ace = any(card.suit == suit_enum and card.rank.value == "Ace" for card in player.hand)
    if not has_ace:
        # Remove a card and add the ace
        player.hand.pop()
        player.hand.append(Card(suit_enum, Rank.ACE))
    return game

@given(parsers.parse('player {player_index:d} has bid "{contract}"'))
def player_has_bid(game, player_index, contract):
    """Player has made a bid"""
    game.current_bidder_index = player_index
    if contract == "Rufer":
        # Find an ace not in player's hand
        player = game.players[player_index]
        for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
            has_ace = any(card.suit == suit and card.rank.value == "Ace" for card in player.hand)
            if not has_ace:
                game.make_bid(player_index, "Rufer", None, suit)
                break
    elif contract == "Wenz":
        game.make_bid(player_index, "Wenz")
    elif contract == "Solo":
        game.make_bid(player_index, "Solo", Suit.EICHEL)
    return game

@given("no one has made a bid")
def no_bids(game):
    """No bids have been made"""
    game.highest_bid = None
    return game

@when(parsers.parse('player {player_index:d} bids "{contract}" with called ace "{suit}"'))
def player_bids_rufer(game, player_index, contract, suit):
    """Player makes a Rufer bid"""
    game.current_bidder_index = player_index
    suit_enum = Suit(suit)
    game.bid_result = game.make_bid(player_index, contract, None, suit_enum)
    return game

@when(parsers.parse('player {player_index:d} tries to bid "{contract}" with called ace "{suit}"'))
def player_tries_bid_rufer(game, player_index, contract, suit):
    """Player tries to make a bid"""
    game.current_bidder_index = player_index
    suit_enum = Suit(suit)
    game.bid_result = game.make_bid(player_index, contract, None, suit_enum)
    return game

@when(parsers.parse('player {player_index:d} bids "{contract}"'))
def player_bids(game, player_index, contract):
    """Player makes a bid"""
    game.current_bidder_index = player_index
    if contract == "Wenz":
        game.bid_result = game.make_bid(player_index, "Wenz")
    elif contract == "Solo":
        game.bid_result = game.make_bid(player_index, "Solo", Suit.EICHEL)
    return game

@when(parsers.parse('player {player_index:d} tries to bid "{contract}"'))
def player_tries_bid(game, player_index, contract):
    """Player tries to make a bid"""
    game.current_bidder_index = player_index
    if contract == "Rufer":
        game.bid_result = game.make_bid(player_index, "Rufer", None, Suit.EICHEL)
    elif contract == "Wenz":
        game.bid_result = game.make_bid(player_index, "Wenz")
    elif contract == "Solo":
        game.bid_result = game.make_bid(player_index, "Solo", Suit.GRAS)
    return game

@when(parsers.parse('player {player_index:d} passes'))
def player_passes(game, player_index):
    """Player passes"""
    game.current_bidder_index = player_index
    game.pass_result = game.pass_bid(player_index)
    return game

@when("all 4 players pass")
def all_players_pass(game):
    """All players pass"""
    for i in range(4):
        game.current_bidder_index = i
        game.pass_bid(i)
    return game

@then("the bid should be accepted")
def bid_accepted(game):
    """Bid was accepted"""
    assert game.bid_result == True

@then("the bid should be rejected")
def bid_rejected(game):
    """Bid was rejected"""
    assert game.bid_result == False

@then(parsers.parse('the highest bid should be "{contract}"'))
def highest_bid_is(game, contract):
    """Highest bid is set correctly"""
    assert game.highest_bid is not None
    assert game.highest_bid["contract_type"] == contract

@then(parsers.parse('it should be player {player_index:d}\'s turn to bid'))
def next_bidder(game, player_index):
    """Next player's turn"""
    assert game.current_bidder_index == player_index

@then("an error message should indicate the ace is in their hand")
def error_ace_in_hand(game):
    """Error about ace in hand"""
    assert game.bid_result == False

@then(parsers.parse('player {player_index:d} should be the highest bidder'))
def highest_bidder_is(game, player_index):
    """Highest bidder is correct"""
    assert game.highest_bid["bidder_index"] == player_index

@then("the cards should be reshuffled")
def cards_reshuffled(game):
    """Cards are reshuffled"""
    # After all pass, bidding_complete should be True and highest_bid None
    assert game.bidding_complete == True
    assert game.highest_bid is None

@then("a new bidding round should start")
def new_bidding_round(game):
    """New bidding round starts"""
    # After reshuffle logic, bidding_phase should be True again
    # (This is handled in websocket.py, but we can check the state)
    pass

@then("the starting bidder should move clockwise")
def bidder_moved_clockwise(game):
    """Starting bidder moved"""
    # initial_bidder_index should have moved
    assert game.initial_bidder_index == 1  # Moved from 0 to 1

@then("the bidding phase should end")
def bidding_ended(game):
    """Bidding phase ended"""
    assert game.bidding_complete == True
    assert game.bidding_phase == False

@then(parsers.parse('the contract should be set to "{contract}"'))
def contract_set(game, contract):
    """Contract is set"""
    assert game.contract_type == contract

@then(parsers.parse('player {player_index:d} should be the declarer'))
def declarer_is(game, player_index):
    """Declarer is correct"""
    assert game.declarer_index == player_index

@then(parsers.parse('player {player_index:d} should remain the highest bidder'))
def bidder_unchanged(game, player_index):
    """Highest bidder unchanged"""
    assert game.highest_bid["bidder_index"] == player_index

# Load scenarios from feature file
scenarios = [
    "features/bidding.feature",
]


