"""
F1 Fuel and Weight Model

This module models fuel consumption, weight effects on lap time,
and fuel-saving modes for race strategy optimization.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FuelState:
    """Current fuel state of the car"""
    fuel_load: float  # kg
    fuel_flow_rate: float  # kg/lap
    fuel_mode: str  # "NORMAL", "SAVING", "PUSH"


class FuelModel:
    """
    Models fuel consumption and its effect on car performance.
    
    Key factors:
    - Fuel weight effect: ~0.03s per kg per lap
    - Fuel consumption: ~1.5-1.8 kg/lap depending on mode
    - Maximum fuel load: 110 kg (FIA regulation)
    - Fuel saving: can reduce consumption by 10-15%
    """
    
    # FIA regulations
    MAX_FUEL_LOAD = 110.0  # kg
    MAX_FUEL_FLOW = 100.0  # kg/hour (not enforced in this model)
    
    # Fuel consumption rates by mode (kg/lap)
    FUEL_CONSUMPTION = {
        "PUSH": 1.8,      # Maximum attack mode
        "NORMAL": 1.6,    # Standard racing mode
        "SAVING": 1.35,   # Fuel-saving mode
    }
    
    # Lap time effect (seconds per kg of fuel)
    FUEL_WEIGHT_EFFECT = 0.03
    
    # Lap time penalty for fuel-saving mode (seconds)
    FUEL_SAVE_PENALTY = 0.4
    
    def __init__(
        self,
        race_laps: int,
        base_lap_time: float = 90.0,
        initial_fuel: float = 110.0
    ):
        """
        Initialize fuel model.
        
        Args:
            race_laps: Total number of race laps
            base_lap_time: Baseline lap time (seconds) with full fuel
            initial_fuel: Starting fuel load (kg)
        """
        self.race_laps = race_laps
        self.base_lap_time = base_lap_time
        self.initial_fuel = min(initial_fuel, self.MAX_FUEL_LOAD)
        
    def calculate_fuel_effect(self, fuel_load: float) -> float:
        """
        Calculate lap time delta due to fuel weight.
        
        Args:
            fuel_load: Current fuel load in kg
            
        Returns:
            Time delta in seconds (positive = slower)
        """
        return fuel_load * self.FUEL_WEIGHT_EFFECT
    
    def predict_lap_time_with_fuel(
        self,
        base_lap_time: float,
        fuel_load: float,
        fuel_mode: str = "NORMAL"
    ) -> float:
        """
        Predict lap time including fuel weight and mode effects.
        
        Args:
            base_lap_time: Base lap time without fuel consideration
            fuel_load: Current fuel load in kg
            fuel_mode: Fuel mode ("NORMAL", "SAVING", "PUSH")
            
        Returns:
            Adjusted lap time in seconds
        """
        # Fuel weight effect
        fuel_delta = self.calculate_fuel_effect(fuel_load)
        
        # Fuel mode effect
        mode_delta = 0.0
        if fuel_mode == "SAVING":
            mode_delta = self.FUEL_SAVE_PENALTY
        elif fuel_mode == "PUSH":
            mode_delta = -0.2  # Slightly faster in push mode
        
        return base_lap_time + fuel_delta + mode_delta
    
    def calculate_required_fuel(
        self,
        race_laps: int,
        fuel_mode: str = "NORMAL",
        safety_margin: float = 2.0
    ) -> float:
        """
        Calculate minimum fuel required for race distance.
        
        Args:
            race_laps: Number of laps to complete
            fuel_mode: Fuel consumption mode
            safety_margin: Extra fuel for safety (kg)
            
        Returns:
            Required fuel load in kg
        """
        consumption_rate = self.FUEL_CONSUMPTION[fuel_mode]
        required_fuel = race_laps * consumption_rate + safety_margin
        
        return min(required_fuel, self.MAX_FUEL_LOAD)
    
    def simulate_fuel_stint(
        self,
        stint_laps: int,
        initial_fuel: float,
        fuel_mode: str = "NORMAL",
        base_lap_time: float = 90.0
    ) -> List[Dict[str, float]]:
        """
        Simulate fuel consumption and lap times over a stint.
        
        Args:
            stint_laps: Number of laps in stint
            initial_fuel: Starting fuel load (kg)
            fuel_mode: Fuel consumption mode
            base_lap_time: Base lap time without fuel effect
            
        Returns:
            List of lap-by-lap fuel and time data
        """
        consumption_rate = self.FUEL_CONSUMPTION[fuel_mode]
        fuel_load = initial_fuel
        
        stint_data = []
        
        for lap in range(1, stint_laps + 1):
            # Calculate lap time with current fuel load
            lap_time = self.predict_lap_time_with_fuel(
                base_lap_time,
                fuel_load,
                fuel_mode
            )
            
            stint_data.append({
                'lap': lap,
                'fuel_load': fuel_load,
                'fuel_mode': fuel_mode,
                'lap_time': lap_time,
                'fuel_effect': self.calculate_fuel_effect(fuel_load)
            })
            
            # Consume fuel
            fuel_load = max(0.0, fuel_load - consumption_rate)
        
        return stint_data
    
    def optimize_fuel_strategy(
        self,
        race_laps: int,
        target_finish_fuel: float = 0.0
    ) -> Dict[str, any]:
        """
        Optimize fuel strategy to minimize race time.
        
        This calculates the optimal fuel load and determines if/when
        fuel-saving mode should be used.
        
        Args:
            race_laps: Total race laps
            target_finish_fuel: Minimum fuel at finish (kg)
            
        Returns:
            Dictionary with optimal fuel strategy
        """
        # Calculate minimum fuel needed
        min_fuel_normal = self.calculate_required_fuel(race_laps, "NORMAL", 0.0)
        min_fuel_saving = self.calculate_required_fuel(race_laps, "SAVING", 0.0)
        
        # Strategy 1: Start with less fuel, use normal mode
        strategy_1_fuel = min_fuel_normal + target_finish_fuel
        
        # Strategy 2: Start with max fuel, potentially use fuel-saving
        strategy_2_fuel = self.MAX_FUEL_LOAD
        
        # Simulate both strategies
        time_1 = self._simulate_race_fuel(race_laps, strategy_1_fuel, "NORMAL")
        time_2 = self._simulate_race_fuel(race_laps, strategy_2_fuel, "NORMAL")
        
        # Determine optimal
        if time_1 < time_2:
            optimal_strategy = {
                'initial_fuel': strategy_1_fuel,
                'fuel_mode': 'NORMAL',
                'estimated_time': time_1,
                'fuel_at_finish': target_finish_fuel,
                'strategy': 'Minimum fuel load, normal mode throughout'
            }
        else:
            optimal_strategy = {
                'initial_fuel': strategy_2_fuel,
                'fuel_mode': 'NORMAL',
                'estimated_time': time_2,
                'fuel_at_finish': strategy_2_fuel - (race_laps * self.FUEL_CONSUMPTION['NORMAL']),
                'strategy': 'Maximum fuel load, normal mode throughout'
            }
        
        return optimal_strategy
    
    def _simulate_race_fuel(
        self,
        race_laps: int,
        initial_fuel: float,
        fuel_mode: str
    ) -> float:
        """
        Internal method to simulate total race time with fuel effects.
        
        Args:
            race_laps: Number of race laps
            initial_fuel: Starting fuel load
            fuel_mode: Fuel consumption mode
            
        Returns:
            Total race time in seconds
        """
        stint_data = self.simulate_fuel_stint(
            race_laps,
            initial_fuel,
            fuel_mode,
            self.base_lap_time
        )
        
        total_time = sum(lap['lap_time'] for lap in stint_data)
        return total_time
    
    def calculate_fuel_saving_benefit(
        self,
        current_lap: int,
        remaining_laps: int,
        current_fuel: float
    ) -> Dict[str, float]:
        """
        Calculate benefit of switching to fuel-saving mode.
        
        Args:
            current_lap: Current race lap
            remaining_laps: Laps remaining in race
            current_fuel: Current fuel load (kg)
            
        Returns:
            Dictionary with fuel-saving analysis
        """
        # Calculate fuel needed to finish
        fuel_needed_normal = remaining_laps * self.FUEL_CONSUMPTION['NORMAL']
        fuel_needed_saving = remaining_laps * self.FUEL_CONSUMPTION['SAVING']
        
        # Fuel deficit/surplus
        fuel_margin_normal = current_fuel - fuel_needed_normal
        fuel_margin_saving = current_fuel - fuel_needed_saving
        
        # Determine if fuel-saving is necessary
        must_save = fuel_margin_normal < 0
        
        # Calculate time cost of fuel-saving
        if must_save:
            # Must save fuel - calculate how many laps
            laps_to_save = int(np.ceil(abs(fuel_margin_normal) / 
                              (self.FUEL_CONSUMPTION['NORMAL'] - self.FUEL_CONSUMPTION['SAVING'])))
            time_cost = laps_to_save * self.FUEL_SAVE_PENALTY
        else:
            laps_to_save = 0
            time_cost = 0.0
        
        return {
            'must_save_fuel': must_save,
            'fuel_margin_normal': fuel_margin_normal,
            'fuel_margin_saving': fuel_margin_saving,
            'laps_to_save': laps_to_save,
            'time_cost': time_cost,
            'recommendation': 'SAVING' if must_save else 'NORMAL'
        }


class ERSModel:
    """
    Energy Recovery System (ERS) deployment model.
    
    ERS provides ~160 HP boost for up to 33 seconds per lap.
    Strategic deployment can gain 0.3-0.5s per lap.
    """
    
    MAX_ERS_PER_LAP = 33.0  # seconds of deployment per lap
    ERS_LAP_TIME_GAIN = 0.4  # seconds gained with full deployment
    
    def __init__(self):
        """Initialize ERS model."""
        self.ers_available = self.MAX_ERS_PER_LAP
    
    def calculate_ers_effect(self, deployment_percentage: float) -> float:
        """
        Calculate lap time gain from ERS deployment.
        
        Args:
            deployment_percentage: Percentage of available ERS used (0-100)
            
        Returns:
            Lap time gain in seconds (negative = faster)
        """
        deployment_factor = deployment_percentage / 100.0
        return -self.ERS_LAP_TIME_GAIN * deployment_factor
    
    def optimal_ers_deployment(
        self,
        track_characteristics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate optimal ERS deployment strategy for a track.
        
        Args:
            track_characteristics: Dict with 'straights', 'corners', etc.
            
        Returns:
            Dictionary with deployment recommendations
        """
        # Simplified model: deploy more on tracks with long straights
        straight_factor = track_characteristics.get('straight_percentage', 0.4)
        
        optimal_deployment = min(100.0, 70.0 + straight_factor * 50.0)
        
        return {
            'deployment_percentage': optimal_deployment,
            'lap_time_gain': self.calculate_ers_effect(optimal_deployment),
            'strategy': 'Deploy heavily on straights for overtaking'
        }


if __name__ == "__main__":
    # Example usage
    print("=== F1 Fuel Model Demo ===\n")
    
    # Initialize fuel model for a 57-lap race
    fuel_model = FuelModel(
        race_laps=57,
        base_lap_time=78.5,
        initial_fuel=110.0
    )
    
    # Calculate required fuel
    required = fuel_model.calculate_required_fuel(57, "NORMAL")
    print(f"Required fuel for 57 laps: {required:.1f} kg")
    print(f"Maximum allowed: {FuelModel.MAX_FUEL_LOAD} kg\n")
    
    # Simulate a 20-lap stint
    print("=== 20-Lap Stint Simulation ===")
    stint_data = fuel_model.simulate_fuel_stint(
        stint_laps=20,
        initial_fuel=110.0,
        fuel_mode="NORMAL",
        base_lap_time=78.5
    )
    
    # Show key laps
    for lap_data in [stint_data[0], stint_data[9], stint_data[19]]:
        print(f"Lap {lap_data['lap']:2d}: "
              f"Fuel: {lap_data['fuel_load']:5.1f} kg, "
              f"Time: {lap_data['lap_time']:.3f}s "
              f"(+{lap_data['fuel_effect']:.3f}s from fuel)")
    
    # Fuel-saving analysis
    print("\n=== Fuel-Saving Analysis (Lap 40) ===")
    saving_analysis = fuel_model.calculate_fuel_saving_benefit(
        current_lap=40,
        remaining_laps=17,
        current_fuel=25.0
    )
    
    print(f"Must save fuel: {saving_analysis['must_save_fuel']}")
    print(f"Fuel margin (normal mode): {saving_analysis['fuel_margin_normal']:+.1f} kg")
    print(f"Laps to save: {saving_analysis['laps_to_save']}")
    print(f"Time cost: {saving_analysis['time_cost']:.1f}s")
    print(f"Recommendation: {saving_analysis['recommendation']} mode")
    
    # ERS model demo
    print("\n=== ERS Deployment ===")
    ers_model = ERSModel()
    ers_strategy = ers_model.optimal_ers_deployment({
        'straight_percentage': 0.45
    })
    
    print(f"Optimal deployment: {ers_strategy['deployment_percentage']:.0f}%")
    print(f"Lap time gain: {ers_strategy['lap_time_gain']:.3f}s")
