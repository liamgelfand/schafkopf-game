from typing import List, Dict
from app.models.player import Player
from app.game_logic.contracts import Contract

def calculate_round_score(
    contract: Contract,
    players: List[Player],
    all_tricks: List[List]
) -> Dict:
    """
    Calculate final scores for a round
    
    Args:
        contract: The contract being played
        players: List of all players
        all_tricks: List of all tricks won (8 total)
    
    Returns:
        Dictionary with scoring information
    """
    declarer = players[contract.declarer_index]
    declarer_points = declarer.points
    
    # Calculate team points
    if contract.contract_type == "Rufer" and contract.partner_index is not None:
        partner = players[contract.partner_index]
        team_points = declarer_points + partner.points
        opponents_points = sum(
            p.points for i, p in enumerate(players)
            if i != contract.declarer_index and i != contract.partner_index
        )
    else:
        # Solo game
        team_points = declarer_points
        opponents_points = sum(
            p.points for i, p in enumerate(players)
            if i != contract.declarer_index
        )
    
    # Determine win/loss
    won = team_points >= 61
    
    # Check for Schneider (91+ points)
    schneider = team_points >= 91
    
    # Check for Schwarz (all 8 tricks)
    declarer_tricks = len(declarer.tricks_won)
    schwarz = declarer_tricks == 8
    
    # In partnership, check if partner has all tricks
    if contract.contract_type == "Rufer" and contract.partner_index is not None:
        partner_tricks = len(players[contract.partner_index].tricks_won)
        schwarz = declarer_tricks + partner_tricks == 8
    
    return {
        "declarer_points": declarer_points,
        "team_points": team_points,
        "opponents_points": opponents_points,
        "won": won,
        "schneider": schneider,
        "schwarz": schwarz,
        "declarer_tricks": declarer_tricks,
    }

def calculate_game_points(round_score: Dict, contract_type: str) -> int:
    """
    Calculate game points based on round score and contract type
    
    Args:
        round_score: Result from calculate_round_score
        contract_type: Type of contract played
    
    Returns:
        Game points awarded
    """
    base_points = {
        "Rufer": 1,
        "Wenz": 2,
        "Solo": 3,
    }
    
    if not round_score["won"]:
        return -base_points[contract_type]
    
    points = base_points[contract_type]
    
    if round_score["schneider"]:
        points *= 2
    
    if round_score["schwarz"]:
        points *= 2
    
    return points


