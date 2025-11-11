"""
F1 Pit Stop Strategy Optimizer

This module implements pit stop strategy optimization using both deterministic
and Monte Carlo simulation approaches. It calculates optimal pit windows,
undercut/overcut opportunities, and multi-stop strategy comparisons.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import itertools

from engine.tire_model import TireCompound, TireDegradationModel


@dataclass
class PitStopEvent:
    """Represents a pit stop event"""
    lap: int
    in_compound: TireCompound
    out_compound: TireCompound
    pit_loss_time: float = 22.0  # Typical pit loss (including in/out laps)
    tire_age_in: int = 0


@dataclass
class RaceStrategy:
    """Complete race strategy with multiple stints"""
    pit_stops: List[PitStopEvent]
    total_race_time: float
    stint_compounds: List[TireCompound]
    risk_score: float = 0.0  # 0-100, higher = riskier
    
    def __str__(self) -> str:
        stints = " → ".join([c.value[0] for c in self.stint_compounds])
        stops = len(self.pit_stops)
        return f"{stops}-stop ({stints}): {self.total_race_time:.1f}s"


class PitStrategyOptimizer:
    """
    Optimizes pit stop strategy for a race.
    
    Considers:
    - Tire degradation curves
    - Pit stop time loss
    - Undercut/overcut opportunities
    - Safety car probability
    - Track position vs tire advantage trade-offs
    """
    
    # F1 regulations: must use 2 different compounds (dry race)
    MANDATORY_COMPOUNDS = 2
    
    # Typical pit stop time losses
    PIT_LOSS_BASE = 22.0  # seconds (stationary + in/out laps)
    PIT_LOSS_VARIANCE = 2.0  # standard deviation for Monte Carlo
    
    def __init__(
        self,
        tire_model: TireDegradationModel,
        race_laps: int,
        track_name: str = "Generic Circuit",
        pit_loss_time: float = 22.0
    ):
        """
        Initialize pit strategy optimizer.
        
        Args:
            tire_model: Tire degradation model instance
            race_laps: Total number of race laps
            track_name: Name of the circuit
            pit_loss_time: Time lost per pit stop (seconds)
        """
        self.tire_model = tire_model
        self.race_laps = race_laps
        self.track_name = track_name
        self.pit_loss_time = pit_loss_time
        
    def simulate_strategy(
        self,
        pit_stops: List[PitStopEvent],
        initial_fuel: float = 110.0,
        fuel_per_lap: float = 1.6
    ) -> float:
        """
        Simulate a complete race strategy and return total time.
        
        Args:
            pit_stops: List of planned pit stops
            initial_fuel: Starting fuel load in kg
            fuel_per_lap: Fuel consumption per lap in kg
            
        Returns:
            Total race time in seconds
        """
        total_time = 0.0
        current_lap = 1
        current_compound = pit_stops[0].out_compound if pit_stops else TireCompound.MEDIUM
        tire_age = 0
        fuel_load = initial_fuel
        
        # Sort pit stops by lap
        sorted_stops = sorted(pit_stops, key=lambda x: x.lap)
        pit_index = 0
        
        for lap in range(1, self.race_laps + 1):
            # Check if we pit this lap
            if pit_index < len(sorted_stops) and lap == sorted_stops[pit_index].lap:
                # Add pit stop time
                total_time += self.pit_loss_time
                
                # Change compound and reset tire age
                current_compound = sorted_stops[pit_index].out_compound
                tire_age = 0
                pit_index += 1
            
            # Simulate lap time
            tire_age += 1
            lap_time = self.tire_model.predict_lap_time(
                current_compound,
                tire_age,
                fuel_load
            )
            
            total_time += lap_time
            fuel_load = max(0, fuel_load - fuel_per_lap)
        
        return total_time
    
    def generate_strategy_combinations(
        self,
        max_stops: int = 3,
        available_compounds: Optional[List[TireCompound]] = None
    ) -> List[List[PitStopEvent]]:
        """
        Generate all viable strategy combinations.
        
        Args:
            max_stops: Maximum number of pit stops to consider
            available_compounds: List of available tire compounds
            
        Returns:
            List of strategy combinations (each is a list of PitStopEvents)
        """
        if available_compounds is None:
            available_compounds = [
                TireCompound.SOFT,
                TireCompound.MEDIUM,
                TireCompound.HARD
            ]
        
        strategies = []
        
        # Generate strategies for 1, 2, and 3 stops
        for num_stops in range(1, max_stops + 1):
            # Generate compound sequences (must use at least 2 different compounds)
            compound_sequences = self._generate_compound_sequences(
                num_stops + 1,  # stints = stops + 1
                available_compounds
            )
            
            for compounds in compound_sequences:
                # Generate pit lap combinations for this compound sequence
                pit_lap_combos = self._generate_pit_lap_combinations(
                    num_stops,
                    compounds
                )
                
                for pit_laps in pit_lap_combos:
                    pit_stops = []
                    for i, lap in enumerate(pit_laps):
                        pit_stops.append(PitStopEvent(
                            lap=lap,
                            in_compound=compounds[i],
                            out_compound=compounds[i + 1],
                            pit_loss_time=self.pit_loss_time
                        ))
                    strategies.append(pit_stops)
        
        return strategies
    
    def _generate_compound_sequences(
        self,
        num_stints: int,
        available_compounds: List[TireCompound]
    ) -> List[List[TireCompound]]:
        """Generate compound sequences that satisfy F1 regulations."""
        sequences = []
        
        # Generate all possible sequences
        for sequence in itertools.product(available_compounds, repeat=num_stints):
            # Must use at least 2 different compounds
            if len(set(sequence)) >= self.MANDATORY_COMPOUNDS:
                sequences.append(list(sequence))
        
        return sequences
    
    def _generate_pit_lap_combinations(
        self,
        num_stops: int,
        compounds: List[TireCompound]
    ) -> List[List[int]]:
        """
        Generate realistic pit lap combinations based on tire characteristics.
        
        Args:
            num_stops: Number of pit stops
            compounds: Compound sequence for stints
            
        Returns:
            List of pit lap combinations
        """
        combinations = []
        
        if num_stops == 1:
            # 1-stop: pit between lap 15 and 45
            for lap in range(15, min(46, self.race_laps - 10)):
                combinations.append([lap])
        
        elif num_stops == 2:
            # 2-stop: divide race into thirds roughly
            for lap1 in range(12, min(30, self.race_laps // 3 + 5)):
                for lap2 in range(lap1 + 12, min(self.race_laps - 5, lap1 + 25)):
                    combinations.append([lap1, lap2])
        
        elif num_stops == 3:
            # 3-stop: divide into quarters
            for lap1 in range(10, min(20, self.race_laps // 4 + 3)):
                for lap2 in range(lap1 + 10, min(lap1 + 18, self.race_laps // 2)):
                    for lap3 in range(lap2 + 10, min(self.race_laps - 5, lap2 + 18)):
                        combinations.append([lap1, lap2, lap3])
        
        return combinations
    
    def optimize_strategy(
        self,
        max_stops: int = 3,
        available_compounds: Optional[List[TireCompound]] = None,
        top_n: int = 5
    ) -> List[RaceStrategy]:
        """
        Find optimal race strategies using deterministic simulation.
        
        Args:
            max_stops: Maximum number of pit stops to consider
            available_compounds: List of available tire compounds
            top_n: Number of top strategies to return
            
        Returns:
            List of top N strategies sorted by race time
        """
        print(f"Optimizing strategy for {self.race_laps}-lap race at {self.track_name}...")
        
        # Generate all strategy combinations
        strategy_combos = self.generate_strategy_combinations(max_stops, available_compounds)
        print(f"Evaluating {len(strategy_combos)} strategy combinations...")
        
        results = []
        
        for pit_stops in strategy_combos:
            # Simulate this strategy
            race_time = self.simulate_strategy(pit_stops)
            
            # Extract stint compounds
            stint_compounds = [pit_stops[0].out_compound]
            for stop in pit_stops:
                stint_compounds.append(stop.out_compound)
            
            # Calculate risk score (more stops = higher risk)
            risk_score = len(pit_stops) * 15 + np.random.uniform(0, 10)
            
            strategy = RaceStrategy(
                pit_stops=pit_stops,
                total_race_time=race_time,
                stint_compounds=stint_compounds,
                risk_score=risk_score
            )
            
            results.append(strategy)
        
        # Sort by race time
        results.sort(key=lambda x: x.total_race_time)
        
        return results[:top_n]
    
    def calculate_undercut_advantage(
        self,
        current_lap: int,
        my_tire_age: int,
        my_compound: TireCompound,
        opponent_tire_age: int,
        opponent_compound: TireCompound,
        gap_seconds: float
    ) -> Dict[str, float]:
        """
        Calculate undercut advantage if we pit now vs opponent pitting next lap.
        
        Args:
            current_lap: Current race lap
            my_tire_age: Age of my current tires
            my_compound: My current tire compound
            opponent_tire_age: Age of opponent's tires
            opponent_compound: Opponent's tire compound
            gap_seconds: Current gap to opponent (positive = we're ahead)
            
        Returns:
            Dictionary with undercut analysis
        """
        # Scenario 1: We pit now, opponent stays out
        my_time_pit_lap = self.pit_loss_time
        opponent_time_pit_lap = self.tire_model.predict_lap_time(
            opponent_compound,
            opponent_tire_age + 1
        )
        
        # Next lap: we're on fresh tires, opponent on old tires
        my_time_next_lap = self.tire_model.predict_lap_time(my_compound, 1)
        opponent_time_next_lap = self.tire_model.predict_lap_time(
            opponent_compound,
            opponent_tire_age + 2
        )
        
        # Calculate gap change over 2 laps
        my_total = my_time_pit_lap + my_time_next_lap
        opponent_total = opponent_time_pit_lap + opponent_time_next_lap
        
        time_gained = opponent_total - my_total
        new_gap = gap_seconds + time_gained
        
        # Undercut successful if we gain track position
        undercut_success = new_gap < -1.0  # Need 1s buffer for safety
        
        return {
            'time_gained': time_gained,
            'new_gap': new_gap,
            'undercut_success': undercut_success,
            'advantage_per_lap': time_gained / 2
        }
    
    def monte_carlo_simulation(
        self,
        strategy: RaceStrategy,
        num_simulations: int = 1000,
        safety_car_probability: float = 0.3
    ) -> Dict[str, float]:
        """
        Run Monte Carlo simulation to assess strategy robustness.
        
        Args:
            strategy: Strategy to simulate
            num_simulations: Number of Monte Carlo runs
            safety_car_probability: Probability of safety car during race
            
        Returns:
            Dictionary with statistical results
        """
        race_times = []
        
        for _ in range(num_simulations):
            # Add randomness to pit stop times
            modified_stops = []
            for stop in strategy.pit_stops:
                pit_loss = np.random.normal(self.pit_loss_time, self.PIT_LOSS_VARIANCE)
                modified_stops.append(PitStopEvent(
                    lap=stop.lap,
                    in_compound=stop.in_compound,
                    out_compound=stop.out_compound,
                    pit_loss_time=max(18.0, pit_loss)  # Minimum 18s
                ))
            
            # Simulate with randomness
            race_time = self.simulate_strategy(modified_stops)
            
            # Random safety car effect (can help or hurt)
            if np.random.random() < safety_car_probability:
                # Safety car: random effect between -15s and +15s
                sc_effect = np.random.uniform(-15, 15)
                race_time += sc_effect
            
            race_times.append(race_time)
        
        race_times = np.array(race_times)
        
        return {
            'mean_time': np.mean(race_times),
            'std_dev': np.std(race_times),
            'best_case': np.min(race_times),
            'worst_case': np.max(race_times),
            'p10': np.percentile(race_times, 10),
            'p90': np.percentile(race_times, 90)
        }


if __name__ == "__main__":
    # Example usage
    print("=== F1 Pit Strategy Optimizer Demo ===\n")
    
    # Initialize tire model
    tire_model = TireDegradationModel(
        track_temp=28.0,
        track_abrasiveness=1.0,
        base_lap_time=78.5  # Bahrain-like lap time
    )
    
    # Initialize optimizer for a 57-lap race (Bahrain GP)
    optimizer = PitStrategyOptimizer(
        tire_model=tire_model,
        race_laps=57,
        track_name="Bahrain International Circuit",
        pit_loss_time=22.0
    )
    
    # Find optimal strategies
    top_strategies = optimizer.optimize_strategy(max_stops=2, top_n=5)
    
    print("\n=== Top 5 Strategies ===")
    for i, strategy in enumerate(top_strategies, 1):
        print(f"\n{i}. {strategy}")
        print(f"   Risk Score: {strategy.risk_score:.1f}/100")
        
        # Run Monte Carlo for top strategy
        if i == 1:
            print("\n   Monte Carlo Analysis (1000 simulations):")
            mc_results = optimizer.monte_carlo_simulation(strategy)
            print(f"   Mean: {mc_results['mean_time']:.1f}s")
            print(f"   Std Dev: {mc_results['std_dev']:.1f}s")
            print(f"   Best Case: {mc_results['best_case']:.1f}s")
            print(f"   Worst Case: {mc_results['worst_case']:.1f}s")
    
    # Undercut analysis example
    print("\n\n=== Undercut Analysis ===")
    undercut = optimizer.calculate_undercut_advantage(
        current_lap=20,
        my_tire_age=15,
        my_compound=TireCompound.MEDIUM,
        opponent_tire_age=15,
        opponent_compound=TireCompound.MEDIUM,
        gap_seconds=2.5
    )
    
    print(f"Current gap: +{2.5:.1f}s")
    print(f"Time gained by undercutting: {undercut['time_gained']:.2f}s")
    print(f"New gap after undercut: {undercut['new_gap']:+.2f}s")
    print(f"Undercut successful: {undercut['undercut_success']}")
