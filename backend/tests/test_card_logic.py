"""Unit tests for card and deck logic"""
import pytest
from app.models.card import Card, Suit, Rank
from app.models.deck import Deck

class TestCardLogic:
    """Test card and deck functionality"""
    
    def test_deck_creation(self):
        """Test that deck has correct number of cards"""
        deck = Deck()
        assert len(deck.cards) == 32
    
    def test_deck_has_all_cards(self):
        """Test that deck contains all required cards"""
        deck = Deck()
        suits = [Suit.EICHEL, Suit.GRAS, Suit.HERZ, Suit.SCHELLEN]
        ranks = [Rank.ACE, Rank.KING, Rank.OBER, Rank.UNTER, Rank.TEN, Rank.NINE, Rank.EIGHT, Rank.SEVEN]
        
        for suit in suits:
            for rank in ranks:
                card = Card(suit, rank)
                assert card in deck.cards
    
    def test_deal_cards(self):
        """Test dealing cards to players"""
        deck = Deck()
        deck.shuffle()
        hands = deck.deal(4)
        
        assert len(hands) == 4
        for hand in hands:
            assert len(hand) == 8
        
        # All cards should be dealt
        total_cards = sum(len(hand) for hand in hands)
        assert total_cards == 32
        assert len(deck.cards) == 0
    
    def test_deck_reset(self):
        """Test resetting deck"""
        deck = Deck()
        deck.shuffle()
        hands = deck.deal(4)
        
        # Reset deck
        deck.reset()
        assert len(deck.cards) == 32
        
        # Should be able to deal again
        hands2 = deck.deal(4)
        assert len(hands2) == 4
    
    def test_card_equality(self):
        """Test card equality"""
        card1 = Card(Suit.EICHEL, Rank.ACE)
        card2 = Card(Suit.EICHEL, Rank.ACE)
        card3 = Card(Suit.GRAS, Rank.ACE)
        
        assert card1 == card2
        assert card1 != card3




