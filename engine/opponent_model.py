"""
F1 Opponent Pace Model

This module models opponent behavior and pace for strategic decision-making.
Includes overtaking difficulty, DRS effects, and competitive positioning.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TeamTier(Enum):
    """Team performance tiers"""
    TOP = "TOP"  # Red Bull, Mercedes, Ferrari
    MIDFIELD = "MIDFIELD"  # McLaren, Aston Martin, Alpine
    BACKMARKER = "BACKMARKER"  # Williams, Alfa Romeo, Haas


@dataclass
class Driver:
    """Driver information and characteristics"""
    name: str
    team: str
    team_tier: TeamTier
    base_pace: float  # Seconds per lap relative to fastest
    consistency: float  # 0-1, higher = more consistent
    overtaking_skill: float  # 0-1, higher = better at overtaking
    tire_management: float  # 0-1, higher = better tire management


@dataclass
class OpponentState:
    """Current state of an opponent"""
    driver: Driver
    position: int
    gap_ahead: float  # seconds
    gap_behind: float  # seconds
    current_tire_compound: str
    tire_age: int
    last_lap_time: float
    estimated_pace: float


class OpponentPaceModel:
    """
    Models opponent pace and behavior for strategic planning.
    
    Key features:
    - Pace prediction based on team, driver, and tire state
    - Overtaking difficulty assessment
    - DRS effect modeling
    - Traffic impact calculation
    """
    
    # DRS lap time advantage (seconds)
    DRS_ADVANTAGE = 0.3
    
    # Overtaking difficulty by track type
    OVERTAKING_DIFFICULTY = {
        "EASY": 0.3,  # Bahrain, Monza
        "MEDIUM": 0.6,  # Most tracks
        "HARD": 0.9,  # Monaco, Hungary
    }
    
    # Team performance deltas (seconds per lap from fastest team)
    TEAM_PACE_DELTA = {
        TeamTier.TOP: 0.0,
        TeamTier.MIDFIELD: 0.8,
        TeamTier.BACKMARKER: 1.5,
    }
    
    def __init__(
        self,
        track_overtaking_difficulty: str = "MEDIUM",
        drs_zones: int = 2
    ):
        """
        Initialize opponent pace model.
        
        Args:
            track_overtaking_difficulty: Track overtaking difficulty
            drs_zones: Number of DRS zones on track
        """
        self.track_difficulty = self.OVERTAKING_DIFFICULTY[track_overtaking_difficulty]
        self.drs_zones = drs_zones
        
    def predict_opponent_pace(
        self,
        opponent: OpponentState,
        track_conditions: Dict[str, float],
        tire_degradation: float = 0.5
    ) -> float:
        """
        Predict opponent's pace for upcoming laps.
        
        Args:
            opponent: Opponent state
            track_conditions: Track condition factors
            tire_degradation: Tire degradation level (0-1)
            
        Returns:
            Predicted lap time in seconds
        """
        # Base pace from team and driver
        base_pace = (
            opponent.driver.base_pace +
            self.TEAM_PACE_DELTA[opponent.driver.team_tier]
        )
        
        # Tire degradation effect (reduced by tire management skill)
        tire_effect = tire_degradation * 3.0 * (1.0 - opponent.driver.tire_management * 0.3)
        
        # Consistency variation
        consistency_var = np.random.normal(0, 0.2 * (1.0 - opponent.driver.consistency))
        
        predicted_pace = base_pace + tire_effect + consistency_var
        
        return predicted_pace
    
    def calculate_overtaking_probability(
        self,
        my_pace: float,
        opponent_pace: float,
        gap_seconds: float,
        my_tire_advantage: float = 0.0,
        laps_available: int = 5
    ) -> Dict[str, float]:
        """
        Calculate probability of overtaking an opponent.
        
        Args:
            my_pace: My lap time (seconds)
            opponent_pace: Opponent's lap time (seconds)
            gap_seconds: Current gap (positive = I'm behind)
            my_tire_advantage: Tire age advantage (seconds per lap)
            laps_available: Number of laps to attempt overtake
            
        Returns:
            Dictionary with overtaking analysis
        """
        # Pace advantage per lap
        pace_advantage = opponent_pace - my_pace + my_tire_advantage
        
        # Laps needed to close gap
        if pace_advantage > 0:
            laps_to_close = gap_seconds / pace_advantage
        else:
            laps_to_close = float('inf')
        
        # Overtaking probability factors
        if laps_to_close <= laps_available:
            # Base probability from pace advantage
            base_prob = min(0.9, pace_advantage / 1.0)  # 1s advantage = 90% prob
            
            # Adjust for track difficulty
            track_factor = 1.0 - self.track_difficulty
            
            # DRS effect
            drs_factor = 1.0 + (self.drs_zones * 0.15)
            
            overtake_prob = base_prob * track_factor * drs_factor
            overtake_prob = min(0.95, max(0.05, overtake_prob))
        else:
            overtake_prob = 0.0
        
        return {
            'overtake_probability': overtake_prob,
            'pace_advantage': pace_advantage,
            'laps_to_close': laps_to_close,
            'can_overtake': laps_to_close <= laps_available,
            'drs_advantage': self.DRS_ADVANTAGE * self.drs_zones
        }
    
    def calculate_undercut_threat(
        self,
        my_tire_age: int,
        opponent_tire_age: int,
        gap_seconds: float,
        my_compound: str,
        opponent_compound: str
    ) -> Dict[str, any]:
        """
        Assess undercut threat from opponent.
        
        Args:
            my_tire_age: Age of my tires (laps)
            opponent_tire_age: Age of opponent's tires (laps)
            gap_seconds: Gap to opponent (positive = I'm ahead)
            my_compound: My tire compound
            opponent_compound: Opponent's tire compound
            
        Returns:
            Dictionary with undercut threat analysis
        """
        # Tire age delta
        tire_age_delta = my_tire_age - opponent_tire_age
        
        # If opponent is on much fresher tires, undercut threat is high
        if tire_age_delta > 5:
            threat_level = "HIGH"
            recommendation = "Consider pitting soon to cover undercut"
        elif tire_age_delta > 2:
            threat_level = "MEDIUM"
            recommendation = "Monitor opponent closely"
        else:
            threat_level = "LOW"
            recommendation = "No immediate threat"
        
        # Estimate time delta from tire age difference
        time_delta_per_lap = tire_age_delta * 0.05  # ~0.05s per lap age difference
        
        # Laps until opponent catches up (if they pit now)
        pit_loss = 22.0
        if time_delta_per_lap > 0:
            laps_to_catch = (gap_seconds + pit_loss) / time_delta_per_lap
        else:
            laps_to_catch = float('inf')
        
        return {
            'threat_level': threat_level,
            'tire_age_delta': tire_age_delta,
            'time_delta_per_lap': time_delta_per_lap,
            'laps_to_catch': laps_to_catch,
            'recommendation': recommendation
        }
    
    def simulate_battle(
        self,
        my_state: Dict[str, float],
        opponent_state: OpponentState,
        num_laps: int = 10
    ) -> List[Dict[str, float]]:
        """
        Simulate a battle with an opponent over multiple laps.
        
        Args:
            my_state: My current state (pace, tire_age, etc.)
            opponent_state: Opponent's state
            num_laps: Number of laps to simulate
            
        Returns:
            List of lap-by-lap battle data
        """
        battle_data = []
        
        my_tire_age = my_state['tire_age']
        opp_tire_age = opponent_state.tire_age
        gap = my_state.get('gap', 1.0)  # Start 1s behind
        
        for lap in range(1, num_laps + 1):
            # Calculate lap times with tire degradation
            my_pace = my_state['base_pace'] + (my_tire_age * 0.05)
            opp_pace = self.predict_opponent_pace(
                opponent_state,
                {},
                tire_degradation=opp_tire_age / 30.0
            )
            
            # Update gap
            gap_change = opp_pace - my_pace
            gap += gap_change
            
            # Check for overtake
            overtaken = False
            if gap <= 0 and gap > -1.0:
                # Within overtaking range
                overtake_analysis = self.calculate_overtaking_probability(
                    my_pace, opp_pace, abs(gap), 0, 1
                )
                if np.random.random() < overtake_analysis['overtake_probability']:
                    overtaken = True
                    gap = -1.0  # Now ahead by 1s
            
            battle_data.append({
                'lap': lap,
                'my_pace': my_pace,
                'opponent_pace': opp_pace,
                'gap': gap,
                'overtaken': overtaken,
                'my_tire_age': my_tire_age,
                'opp_tire_age': opp_tire_age
            })
            
            my_tire_age += 1
            opp_tire_age += 1
        
        return battle_data
    
    def calculate_traffic_impact(
        self,
        position: int,
        total_cars: int = 20,
        lapped_cars_ahead: int = 0
    ) -> float:
        """
        Calculate lap time impact from traffic.
        
        Args:
            position: Current race position
            total_cars: Total cars in race
            lapped_cars_ahead: Number of lapped cars ahead
            
        Returns:
            Time delta in seconds (positive = slower)
        """
        # Leaders have less traffic
        if position <= 3:
            base_traffic = 0.1
        elif position <= 10:
            base_traffic = 0.3
        else:
            base_traffic = 0.5
        
        # Lapped cars add time
        lapped_car_penalty = lapped_cars_ahead * 0.8
        
        total_impact = base_traffic + lapped_car_penalty
        
        return total_impact


class GridPositionModel:
    """
    Models grid position value and strategic implications.
    """
    
    # Average positions gained/lost from each grid position
    EXPECTED_POSITION_CHANGE = {
        1: -0.5,   # Pole usually loses positions
        2: +0.3,
        3: +0.2,
        # ... etc
    }
    
    def __init__(self, track_name: str = "Generic"):
        """
        Initialize grid position model.
        
        Args:
            track_name: Name of the track
        """
        self.track_name = track_name
    
    def calculate_position_value(
        self,
        grid_position: int,
        race_position: int
    ) -> Dict[str, float]:
        """
        Calculate the value of track position vs tire advantage.
        
        Args:
            grid_position: Starting grid position
            race_position: Current race position
            
        Returns:
            Dictionary with position value analysis
        """
        # Points value by position
        points_table = {
            1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
            6: 8, 7: 6, 8: 4, 9: 2, 10: 1
        }
        
        current_points = points_table.get(race_position, 0)
        
        # Estimate points value of track position
        # Each position is worth roughly 2-3 points in midfield
        position_value = current_points
        
        return {
            'current_position': race_position,
            'current_points': current_points,
            'position_value': position_value,
            'positions_gained': grid_position - race_position
        }


if __name__ == "__main__":
    # Example usage
    print("=== F1 Opponent Pace Model Demo ===\n")
    
    # Create sample drivers
    verstappen = Driver(
        name="Max Verstappen",
        team="Red Bull Racing",
        team_tier=TeamTier.TOP,
        base_pace=78.5,
        consistency=0.95,
        overtaking_skill=0.95,
        tire_management=0.90
    )
    
    norris = Driver(
        name="Lando Norris",
        team="McLaren",
        team_tier=TeamTier.MIDFIELD,
        base_pace=79.0,
        consistency=0.88,
        overtaking_skill=0.85,
        tire_management=0.85
    )
    
    # Create opponent state
    opponent = OpponentState(
        driver=verstappen,
        position=1,
        gap_ahead=0.0,
        gap_behind=2.5,
        current_tire_compound="MEDIUM",
        tire_age=15,
        last_lap_time=79.2,
        estimated_pace=79.0
    )
    
    # Initialize model
    pace_model = OpponentPaceModel(
        track_overtaking_difficulty="MEDIUM",
        drs_zones=2
    )
    
    # Predict opponent pace
    print("=== Pace Prediction ===")
    predicted_pace = pace_model.predict_opponent_pace(
        opponent,
        {},
        tire_degradation=0.5
    )
    print(f"{opponent.driver.name}: {predicted_pace:.3f}s (predicted)")
    
    # Overtaking probability
    print("\n=== Overtaking Analysis ===")
    overtake_analysis = pace_model.calculate_overtaking_probability(
        my_pace=78.8,
        opponent_pace=79.2,
        gap_seconds=2.5,
        my_tire_advantage=0.3,
        laps_available=10
    )
    
    print(f"Pace advantage: {overtake_analysis['pace_advantage']:.3f}s/lap")
    print(f"Laps to close gap: {overtake_analysis['laps_to_close']:.1f}")
    print(f"Overtake probability: {overtake_analysis['overtake_probability']:.1%}")
    print(f"Can overtake in 10 laps: {overtake_analysis['can_overtake']}")
    
    # Undercut threat
    print("\n=== Undercut Threat Analysis ===")
    undercut_threat = pace_model.calculate_undercut_threat(
        my_tire_age=20,
        opponent_tire_age=12,
        gap_seconds=3.5,
        my_compound="MEDIUM",
        opponent_compound="MEDIUM"
    )
    
    print(f"Threat level: {undercut_threat['threat_level']}")
    print(f"Tire age delta: {undercut_threat['tire_age_delta']} laps")
    print(f"Time delta per lap: {undercut_threat['time_delta_per_lap']:.3f}s")
    print(f"Recommendation: {undercut_threat['recommendation']}")
    
    # Battle simulation
    print("\n=== Battle Simulation (10 laps) ===")
    my_state = {
        'base_pace': 78.8,
        'tire_age': 10,
        'gap': 2.0
    }
    
    battle = pace_model.simulate_battle(my_state, opponent, num_laps=10)
    
    for lap_data in battle[::3]:  # Show every 3rd lap
        print(f"Lap {lap_data['lap']}: "
              f"Gap: {lap_data['gap']:+.2f}s, "
              f"My pace: {lap_data['my_pace']:.3f}s, "
              f"Opp pace: {lap_data['opponent_pace']:.3f}s")
