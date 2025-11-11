"""
Safety Car and VSC Model

Predicts safety car deployment probability and strategic impact.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SafetyCarType(Enum):
    """Type of safety car intervention"""
    NONE = "NONE"
    VSC = "VSC"  # Virtual Safety Car
    SC = "SC"    # Full Safety Car
    RED_FLAG = "RED_FLAG"


@dataclass
class SafetyCarEvent:
    """Safety car event details"""
    lap_start: int
    lap_end: int
    sc_type: SafetyCarType
    cause: str
    strategic_window: bool  # Whether it creates pit window


class SafetyCarModel:
    """
    Model for predicting and analyzing safety car events.
    
    Based on historical F1 data:
    - ~30% of races have SC/VSC
    - Most common laps: 1-5, 15-35
    - Average duration: 3-5 laps
    - Strategic impact: 20-25s pit advantage
    """
    
    def __init__(
        self,
        race_laps: int,
        track_type: str = "STREET",  # STREET, PERMANENT, HYBRID
        weather_risk: float = 0.1
    ):
        """
        Initialize safety car model.
        
        Args:
            race_laps: Total race laps
            track_type: Type of circuit (affects SC probability)
            weather_risk: Weather-related incident risk (0-1)
        """
        self.race_laps = race_laps
        self.track_type = track_type
        self.weather_risk = weather_risk
        
        # Base probabilities by track type
        self.base_sc_prob = {
            'STREET': 0.45,      # High (Monaco, Singapore, Baku)
            'PERMANENT': 0.20,   # Low (Spa, Silverstone)
            'HYBRID': 0.30       # Medium (Australia, Canada)
        }
        
        # Lap-specific risk factors
        self.lap_risk_multipliers = self._calculate_lap_risks()
    
    def _calculate_lap_risks(self) -> Dict[int, float]:
        """Calculate risk multiplier for each lap"""
        risks = {}
        
        for lap in range(1, self.race_laps + 1):
            if lap == 1:
                # Lap 1 has highest risk
                risks[lap] = 3.0
            elif 2 <= lap <= 5:
                # Early laps still risky
                risks[lap] = 2.0
            elif 15 <= lap <= 35:
                # Mid-race battles
                risks[lap] = 1.5
            elif lap > self.race_laps - 10:
                # Late race desperation
                risks[lap] = 1.8
            else:
                # Normal racing
                risks[lap] = 1.0
        
        return risks
    
    def predict_sc_probability(self, current_lap: int) -> float:
        """
        Predict probability of SC in remaining laps.
        
        Args:
            current_lap: Current race lap
        
        Returns:
            Probability (0-1) of SC occurring
        """
        base_prob = self.base_sc_prob.get(self.track_type, 0.25)
        
        # Adjust for weather
        weather_factor = 1.0 + self.weather_risk
        
        # Calculate remaining risk
        remaining_laps = self.race_laps - current_lap
        if remaining_laps <= 0:
            return 0.0
        
        # Sum risk for remaining laps
        total_risk = sum(
            self.lap_risk_multipliers.get(lap, 1.0)
            for lap in range(current_lap + 1, self.race_laps + 1)
        )
        
        # Normalize
        avg_risk = total_risk / remaining_laps
        
        probability = min(base_prob * weather_factor * avg_risk / 1.5, 0.95)
        
        return probability
    
    def simulate_sc_event(
        self,
        current_lap: int,
        seed: Optional[int] = None
    ) -> Optional[SafetyCarEvent]:
        """
        Simulate whether SC occurs and its characteristics.
        
        Args:
            current_lap: Current race lap
            seed: Random seed
        
        Returns:
            SafetyCarEvent if SC occurs, None otherwise
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Check if SC occurs
        sc_prob = self.predict_sc_probability(current_lap)
        
        if np.random.random() > sc_prob:
            return None
        
        # Determine SC lap (weighted by risk)
        remaining_laps = list(range(current_lap + 1, self.race_laps + 1))
        if not remaining_laps:
            return None
        
        weights = [self.lap_risk_multipliers.get(lap, 1.0) for lap in remaining_laps]
        weights = np.array(weights) / sum(weights)
        
        sc_lap = np.random.choice(remaining_laps, p=weights)
        
        # Determine type (70% SC, 25% VSC, 5% Red Flag)
        sc_type_prob = np.random.random()
        if sc_type_prob < 0.70:
            sc_type = SafetyCarType.SC
            duration = np.random.randint(3, 6)
        elif sc_type_prob < 0.95:
            sc_type = SafetyCarType.VSC
            duration = np.random.randint(2, 4)
        else:
            sc_type = SafetyCarType.RED_FLAG
            duration = np.random.randint(5, 15)
        
        # Determine cause
        causes = [
            "Collision", "Debris", "Mechanical failure",
            "Barrier damage", "Weather", "Track invasion"
        ]
        cause = np.random.choice(causes)
        
        # Strategic window (if SC is long enough and timing is right)
        strategic_window = (
            sc_type in [SafetyCarType.SC, SafetyCarType.RED_FLAG] and
            duration >= 3 and
            10 <= sc_lap <= self.race_laps - 10
        )
        
        event = SafetyCarEvent(
            lap_start=sc_lap,
            lap_end=min(sc_lap + duration, self.race_laps),
            sc_type=sc_type,
            cause=cause,
            strategic_window=strategic_window
        )
        
        return event
    
    def calculate_pit_advantage(
        self,
        sc_event: SafetyCarEvent,
        pit_loss_normal: float = 22.0
    ) -> float:
        """
        Calculate time advantage of pitting under SC.
        
        Args:
            sc_event: Safety car event
            pit_loss_normal: Normal pit loss time
        
        Returns:
            Time saved by pitting under SC (seconds)
        """
        if sc_event.sc_type == SafetyCarType.VSC:
            # VSC: ~40% speed reduction
            vsc_lap_time = pit_loss_normal * 0.6
            advantage = pit_loss_normal - vsc_lap_time
        elif sc_event.sc_type == SafetyCarType.SC:
            # Full SC: pack bunches up
            sc_lap_time = pit_loss_normal * 0.5
            advantage = pit_loss_normal - sc_lap_time
            # Plus benefit of rejoining in pack
            advantage += 5.0
        else:
            # Red flag: free pit stop
            advantage = pit_loss_normal
        
        return advantage
    
    def should_pit_under_sc(
        self,
        sc_event: SafetyCarEvent,
        tire_age: int,
        remaining_laps: int,
        current_position: int
    ) -> Tuple[bool, str]:
        """
        Determine if driver should pit under SC.
        
        Args:
            sc_event: Safety car event
            tire_age: Current tire age (laps)
            remaining_laps: Laps remaining
            current_position: Current position
        
        Returns:
            (should_pit, reason)
        """
        # Don't pit if very few laps remaining
        if remaining_laps < 10:
            return False, "Too few laps remaining"
        
        # Don't pit if tires are very fresh
        if tire_age < 5:
            return False, "Tires too fresh"
        
        # Always pit under red flag if tires are old
        if sc_event.sc_type == SafetyCarType.RED_FLAG and tire_age > 10:
            return True, "Free pit stop under red flag"
        
        # Pit if in strategic window and tires need changing
        if sc_event.strategic_window:
            if tire_age > 15:
                return True, "Tires degraded, SC provides cheap pit"
            elif current_position > 10 and tire_age > 10:
                return True, "Undercut opportunity from midfield"
        
        # VSC: only pit if tires are very old
        if sc_event.sc_type == SafetyCarType.VSC and tire_age > 20:
            return True, "Tires critical, VSC reduces pit loss"
        
        return False, "No strategic benefit"
    
    def analyze_historical_sc_impact(
        self,
        race_data: List[Dict]
    ) -> Dict[str, float]:
        """
        Analyze historical safety car impact.
        
        Args:
            race_data: List of race dictionaries with SC events
        
        Returns:
            Statistics dictionary
        """
        total_races = len(race_data)
        sc_races = sum(1 for race in race_data if race.get('had_sc', False))
        
        avg_sc_lap = np.mean([
            race.get('sc_lap', 0)
            for race in race_data
            if race.get('had_sc', False)
        ]) if sc_races > 0 else 0
        
        avg_duration = np.mean([
            race.get('sc_duration', 0)
            for race in race_data
            if race.get('had_sc', False)
        ]) if sc_races > 0 else 0
        
        stats = {
            'sc_frequency': sc_races / total_races if total_races > 0 else 0,
            'avg_sc_lap': avg_sc_lap,
            'avg_duration': avg_duration,
            'strategic_impact': 0.75  # 75% of SCs create strategic opportunities
        }
        
        return stats


class VSCModel:
    """
    Specialized model for Virtual Safety Car.
    
    VSC characteristics:
    - Drivers must maintain delta time
    - ~35-40% speed reduction
    - Shorter duration than full SC
    - Less strategic impact
    """
    
    def __init__(self):
        """Initialize VSC model"""
        self.speed_reduction = 0.40
        self.avg_duration = 3.0  # laps
    
    def calculate_vsc_lap_time(self, normal_lap_time: float) -> float:
        """Calculate lap time under VSC"""
        return normal_lap_time * (1 + self.speed_reduction)
    
    def calculate_pit_delta(
        self,
        pit_loss_normal: float,
        normal_lap_time: float
    ) -> float:
        """Calculate time lost pitting under VSC vs normal"""
        vsc_lap_time = self.calculate_vsc_lap_time(normal_lap_time)
        
        # Under VSC, pit loss is relative to VSC lap time
        effective_pit_loss = pit_loss_normal - (vsc_lap_time - normal_lap_time)
        
        return effective_pit_loss


if __name__ == "__main__":
    # Test safety car model
    print("Testing Safety Car Model\n")
    
    model = SafetyCarModel(race_laps=57, track_type="STREET", weather_risk=0.1)
    
    # Test probability prediction
    print("SC Probability by Lap:")
    for lap in [1, 10, 20, 30, 40, 50]:
        prob = model.predict_sc_probability(lap)
        print(f"  Lap {lap}: {prob:.1%}")
    
    # Simulate SC events
    print("\nSimulating 5 race scenarios:")
    for i in range(5):
        event = model.simulate_sc_event(current_lap=0, seed=i)
        if event:
            print(f"\n  Race {i+1}: {event.sc_type.value}")
            print(f"    Laps {event.lap_start}-{event.lap_end}")
            print(f"    Cause: {event.cause}")
            print(f"    Strategic: {event.strategic_window}")
            
            advantage = model.calculate_pit_advantage(event)
            print(f"    Pit advantage: {advantage:.1f}s")
        else:
            print(f"\n  Race {i+1}: No SC")
