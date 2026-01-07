Feature: Bidding Phase
  As a player
  I want to bid on contracts during the bidding phase
  So that I can declare what game I want to play

  Background:
    Given a game with 4 players
    And cards have been dealt
    And the bidding phase has started

  Scenario: Player makes a Rufer bid
    Given it is player 0's turn to bid
    And player 0 has no Ace of Eichel in their hand
    When player 0 bids "Rufer" with called ace "Eichel"
    Then the bid should be accepted
    And the highest bid should be "Rufer"
    And it should be player 1's turn to bid

  Scenario: Player tries to call an ace in their hand
    Given it is player 0's turn to bid
    And player 0 has Ace of Eichel in their hand
    When player 0 tries to bid "Rufer" with called ace "Eichel"
    Then the bid should be rejected
    And an error message should indicate the ace is in their hand

  Scenario: Player bids higher contract
    Given player 0 has bid "Rufer"
    And it is player 1's turn to bid
    When player 1 bids "Wenz"
    Then the bid should be accepted
    And the highest bid should be "Wenz"
    And player 1 should be the highest bidder

  Scenario: Player tries to bid lower contract
    Given player 0 has bid "Wenz"
    And it is player 1's turn to bid
    When player 1 tries to bid "Rufer"
    Then the bid should be rejected
    And the highest bid should remain "Wenz"

  Scenario: All players pass with no bid
    Given no one has made a bid
    When all 4 players pass
    Then the cards should be reshuffled
    And a new bidding round should start
    And the starting bidder should move clockwise

  Scenario: Bidding ends after bid and 3 passes
    Given player 0 has bid "Rufer"
    When player 1 passes
    And player 2 passes
    And player 3 passes
    Then the bidding phase should end
    And the contract should be set to "Rufer"
    And player 0 should be the declarer

  Scenario: Same contract type cannot override
    Given player 0 has bid "Solo" with suit "Eichel"
    And it is player 1's turn to bid
    When player 1 tries to bid "Solo" with suit "Gras"
    Then the bid should be rejected
    And player 0 should remain the highest bidder





