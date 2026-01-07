"""Test utilities and helpers for common test operations"""
from typing import Dict, Any, Optional
from app.models.game import Game
from app.models.card import Suit, Rank, Card
from app.models.player import Player
from app.models.deck import Deck


def create_test_game(game_id: str = "test-game", num_players: int = 4) -> Game:
    """Create a test game with players and dealt cards"""
    game = Game(game_id)
    for i in range(num_players):
        game.add_player(f"player{i+1}")
    game.deal_cards()
    return game


def create_test_card(suit: Suit, rank: Rank) -> Card:
    """Create a test card"""
    return Card(suit, rank)


def create_test_hand(cards: list[tuple[Suit, Rank]]) -> list[Card]:
    """Create a test hand from a list of (suit, rank) tuples"""
    return [Card(suit, rank) for suit, rank in cards]


def create_test_player(player_id: int, name: str, hand: Optional[list[Card]] = None) -> Player:
    """Create a test player with optional hand"""
    player = Player(player_id, name)
    if hand:
        player.hand = hand
    return player


def create_test_deck() -> Deck:
    """Create a fresh test deck"""
    deck = Deck()
    deck.shuffle()
    return deck


def get_contract_rank(contract_type: str, trump_suit: Optional[Suit] = None, is_suited: bool = False) -> int:
    """Get contract rank for testing"""
    if contract_type == "Rufer":
        return 1
    elif contract_type == "Wenz":
        return 3 if is_suited else 2
    elif contract_type == "Solo":
        return 4
    return 0


def simulate_bidding_round(game: Game, bids: list[Dict[str, Any]]) -> None:
    """
    Simulate a complete bidding round
    
    Args:
        game: Game instance
        bids: List of bid dictionaries with keys:
            - player_index: int
            - contract_type: str
            - trump_suit: Optional[Suit]
            - called_ace: Optional[Suit]
            - action: "bid" or "pass"
    """
    for bid in bids:
        if bid.get("action") == "pass":
            game.pass_bid(bid["player_index"])
        else:
            game.make_bid(
                bid["player_index"],
                bid["contract_type"],
                bid.get("trump_suit"),
                bid.get("called_ace")
            )


def find_ace_not_in_hand(player: Player, suit: Suit) -> bool:
    """Check if a player has an ace of the given suit"""
    return any(card.suit == suit and card.rank.value == "Ace" for card in player.hand)


def get_ace_not_in_hand(player: Player) -> Optional[Suit]:
    """Find a suit where the player doesn't have the ace (for Rufer testing)"""
    for suit in [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]:
        if not find_ace_not_in_hand(player, suit):
            return suit
    return None




