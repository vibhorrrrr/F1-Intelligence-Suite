"""
F1 Tire Degradation Model

This module implements tire degradation modeling using both physics-based
and machine learning approaches. It simulates how tire performance degrades
over a stint based on compound, track temperature, fuel load, and driving style.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TireCompound(Enum):
    """F1 tire compounds with their characteristics"""
    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    INTERMEDIATE = "INTERMEDIATE"
    WET = "WET"


@dataclass
class TireState:
    """Current state of a tire set"""
    compound: TireCompound
    age_laps: int
    degradation_level: float  # 0.0 (new) to 1.0 (fully degraded)
    temperature: float  # Celsius
    pressure: float  # PSI


class TireDegradationModel:
    """
    Models tire degradation using exponential decay with compound-specific parameters.
    
    The model accounts for:
    - Compound hardness (Soft degrades faster than Hard)
    - Track temperature (higher temp = faster degradation)
    - Fuel load (heavier car = more tire stress)
    - Track characteristics (abrasiveness factor)
    """
    
    # Base degradation rates per lap (% performance loss)
    BASE_DEGRADATION_RATES = {
        TireCompound.SOFT: 0.08,      # ~12-15 lap optimal window
        TireCompound.MEDIUM: 0.05,    # ~20-25 lap optimal window
        TireCompound.HARD: 0.035,     # ~30-35 lap optimal window
        TireCompound.INTERMEDIATE: 0.06,
        TireCompound.WET: 0.04,
    }
    
    # Lap time delta when new (seconds faster than baseline)
    COMPOUND_PACE = {
        TireCompound.SOFT: -0.8,      # Softs are fastest
        TireCompound.MEDIUM: -0.3,
        TireCompound.HARD: 0.0,       # Hard is baseline
        TireCompound.INTERMEDIATE: 2.5,
        TireCompound.WET: 5.0,
    }
    
    def __init__(
        self,
        track_temp: float = 30.0,
        track_abrasiveness: float = 1.0,
        base_lap_time: float = 90.0
    ):
        """
        Initialize tire degradation model.
        
        Args:
            track_temp: Track temperature in Celsius
            track_abrasiveness: Track surface factor (0.8-1.2, 1.0 = average)
            base_lap_time: Baseline lap time in seconds (on Hard tires)
        """
        self.track_temp = track_temp
        self.track_abrasiveness = track_abrasiveness
        self.base_lap_time = base_lap_time
        
    def calculate_degradation(
        self,
        compound: TireCompound,
        lap_number: int,
        fuel_load: float = 100.0
    ) -> float:
        """
        Calculate tire degradation level at a given lap.
        
        Args:
            compound: Tire compound
            lap_number: Number of laps on this tire set
            fuel_load: Current fuel load in kg
            
        Returns:
            Degradation level (0.0 = new, 1.0 = fully degraded)
        
        Raises:
            ValueError: If lap_number is negative
        """
        if lap_number < 0:
            raise ValueError(f"Lap number must be non-negative, got {lap_number}")
        
        base_rate = self.BASE_DEGRADATION_RATES[compound]
        
        # Temperature factor (higher temp = more degradation)
        # Optimal around 25-30°C, increases above and below
        if self.track_temp > 30.0:
            temp_factor = 1.0 + 0.02 * (self.track_temp - 30.0)
        else:
            temp_factor = 1.0 + 0.01 * (30.0 - self.track_temp)
        
        # Fuel load factor (heavier = more degradation)
        fuel_factor = 1.0 + (fuel_load / 110.0) * 0.15
        
        # Combined degradation rate
        effective_rate = base_rate * temp_factor * fuel_factor * self.track_abrasiveness
        
        # Exponential degradation curve (cliff effect after optimal window)
        degradation = 1.0 - np.exp(-effective_rate * lap_number)
        
        return min(degradation, 1.0)
    
    def predict_lap_time(
        self,
        compound: TireCompound,
        lap_number: int,
        fuel_load: float = 100.0,
        traffic_delta: float = 0.0
    ) -> float:
        """
        Predict lap time based on tire state and conditions.
        
        Args:
            compound: Tire compound
            lap_number: Number of laps on this tire set
            fuel_load: Current fuel load in kg
            traffic_delta: Additional time lost to traffic (seconds)
            
        Returns:
            Predicted lap time in seconds
        """
        # Base lap time with compound advantage
        lap_time = self.base_lap_time + self.COMPOUND_PACE[compound]
        
        # Fuel effect (roughly 0.03s per kg)
        fuel_delta = fuel_load * 0.03
        
        # Tire degradation effect
        degradation = self.calculate_degradation(compound, lap_number, fuel_load)
        
        # Degradation adds time (up to 3 seconds on fully worn tires)
        deg_delta = degradation * 3.0
        
        # Cliff effect: after 90% degradation, time loss accelerates
        if degradation > 0.9:
            cliff_factor = (degradation - 0.9) * 10  # 0 to 1
            deg_delta += cliff_factor * 2.0  # Additional 2 seconds at the cliff
        
        total_lap_time = lap_time + fuel_delta + deg_delta + traffic_delta
        
        return total_lap_time
    
    def generate_stint_profile(
        self,
        compound: TireCompound,
        stint_length: int,
        initial_fuel: float = 110.0,
        fuel_per_lap: float = 1.6
    ) -> List[Dict[str, float]]:
        """
        Generate complete stint profile with lap-by-lap predictions.
        
        Args:
            compound: Tire compound
            stint_length: Number of laps in stint
            initial_fuel: Starting fuel load in kg
            fuel_per_lap: Fuel consumption per lap in kg
            
        Returns:
            List of lap data dictionaries
        """
        profile = []
        
        for lap in range(1, stint_length + 1):
            fuel_load = max(0, initial_fuel - (lap - 1) * fuel_per_lap)
            degradation = self.calculate_degradation(compound, lap, fuel_load)
            lap_time = self.predict_lap_time(compound, lap, fuel_load)
            
            profile.append({
                'lap': lap,
                'compound': compound.value,
                'fuel_load': fuel_load,
                'degradation': degradation,
                'lap_time': lap_time,
                'delta_to_new': lap_time - (self.base_lap_time + self.COMPOUND_PACE[compound])
            })
        
        return profile
    
    def optimal_pit_window(
        self,
        compound: TireCompound,
        max_stint_length: int = 40
    ) -> Tuple[int, int]:
        """
        Calculate optimal pit window for a compound.
        
        Args:
            compound: Tire compound
            max_stint_length: Maximum possible stint length
            
        Returns:
            Tuple of (earliest_optimal_lap, latest_optimal_lap)
        """
        # Find when degradation crosses thresholds
        earliest = None
        latest = None
        
        for lap in range(1, max_stint_length + 1):
            deg = self.calculate_degradation(compound, lap)
            
            # Optimal window: 60% to 85% degradation
            if deg >= 0.6 and earliest is None:
                earliest = lap
            if deg >= 0.85 and latest is None:
                latest = lap
                break
        
        if earliest is None:
            earliest = max_stint_length // 2
        if latest is None:
            latest = max_stint_length
        
        return (earliest, latest)


class MLTireDegradationModel:
    """
    Machine learning-based tire degradation model using historical data.
    
    This is a placeholder for future ML implementation using:
    - Random Forest or Gradient Boosting
    - Features: compound, track temp, lap number, fuel load, track characteristics
    - Target: lap time delta
    """
    
    def __init__(self):
        self.model = None
        self.is_trained = False
    
    def train(self, historical_data: List[Dict]) -> None:
        """
        Train ML model on historical race data.
        
        Args:
            historical_data: List of lap records with features and lap times
        """
        # TODO: Implement sklearn RandomForestRegressor or XGBoost
        # Features: compound_encoded, lap_number, fuel_load, track_temp, track_id
        # Target: lap_time
        pass
    
    def predict(self, features: Dict) -> float:
        """
        Predict lap time using trained ML model.
        
        Args:
            features: Dictionary of input features
            
        Returns:
            Predicted lap time
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # TODO: Implement prediction
        return 0.0


if __name__ == "__main__":
    # Example usage and validation
    print("=== F1 Tire Degradation Model Demo ===\n")
    
    # Initialize model for a typical track
    model = TireDegradationModel(
        track_temp=32.0,
        track_abrasiveness=1.1,  # Slightly abrasive (e.g., Silverstone)
        base_lap_time=90.0
    )
    
    # Compare compounds over 30 laps
    compounds = [TireCompound.SOFT, TireCompound.MEDIUM, TireCompound.HARD]
    
    for compound in compounds:
        print(f"\n{compound.value} Tire Profile:")
        print("-" * 50)
        
        profile = model.generate_stint_profile(compound, stint_length=30)
        
        # Show key laps
        for lap_data in [profile[0], profile[9], profile[19], profile[29]]:
            print(f"Lap {lap_data['lap']:2d}: "
                  f"{lap_data['lap_time']:.3f}s "
                  f"(+{lap_data['delta_to_new']:.3f}s) "
                  f"Deg: {lap_data['degradation']:.1%}")
        
        # Optimal pit window
        early, late = model.optimal_pit_window(compound)
        print(f"Optimal pit window: Laps {early}-{late}")
