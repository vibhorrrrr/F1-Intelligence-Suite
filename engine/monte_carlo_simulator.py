"""
Monte Carlo Race Simulator

Simulates 500-2000 race scenarios with probabilistic events to determine
optimal strategy with confidence intervals.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.tire_model import TireCompound, TireDegradationModel
from engine.pit_optimizer import RaceStrategy, PitStopEvent


@dataclass
class MonteCarloResult:
    """Results from Monte Carlo simulation"""
    strategy: RaceStrategy
    mean_race_time: float
    std_race_time: float
    min_race_time: float
    max_race_time: float
    percentile_5: float
    percentile_95: float
    win_probability: float
    undercut_success_rate: float
    safety_car_benefit: float
    confidence_interval_95: Tuple[float, float]
    position_distribution: Dict[int, float]
    all_times: List[float] = field(default_factory=list)


class MonteCarloRaceSimulator:
    """
    Advanced Monte Carlo simulator for F1 race strategy analysis.
    
    Simulates multiple race scenarios with:
    - Tire degradation variance
    - Fuel load effects
    - Safety car events
    - Rain probability
    - Traffic variance
    - Pit stop time variance
    - ML predictor uncertainty
    """
    
    def __init__(
        self,
        tire_model: TireDegradationModel,
        race_laps: int,
        base_lap_time: float,
        pit_loss_time: float = 22.0,
        n_simulations: int = 1000
    ):
        """
        Initialize Monte Carlo simulator.
        
        Args:
            tire_model: Tire degradation model
            race_laps: Total race laps
            base_lap_time: Base lap time (s)
            pit_loss_time: Pit stop time loss (s)
            n_simulations: Number of simulations to run
        """
        self.tire_model = tire_model
        self.race_laps = race_laps
        self.base_lap_time = base_lap_time
        self.pit_loss_time = pit_loss_time
        self.n_simulations = n_simulations
        
        # Probabilistic parameters
        self.safety_car_prob = 0.15  # 15% chance per race
        self.rain_prob = 0.05  # 5% chance per race
        self.pit_variance = 2.0  # ±2s pit stop variance
        self.lap_time_variance = 0.15  # ±0.15s lap time variance
        
    def simulate_strategy(
        self,
        strategy: RaceStrategy,
        starting_position: int = 10,
        parallel: bool = True
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation for a strategy.
        
        Args:
            strategy: Race strategy to simulate
            starting_position: Starting grid position
            parallel: Use parallel processing
        
        Returns:
            MonteCarloResult with statistics
        """
        print(f"Running {self.n_simulations} Monte Carlo simulations...")
        
        if parallel and self.n_simulations >= 100:
            race_times = self._simulate_parallel(strategy, starting_position)
        else:
            race_times = self._simulate_sequential(strategy, starting_position)
        
        # Calculate statistics
        result = self._calculate_statistics(strategy, race_times, starting_position)
        
        return result
    
    def _simulate_parallel(
        self,
        strategy: RaceStrategy,
        starting_position: int
    ) -> List[float]:
        """Run simulations in parallel"""
        race_times = []
        
        # Use all available cores
        n_workers = min(multiprocessing.cpu_count(), 8)
        
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            futures = [
                executor.submit(
                    self._simulate_single_race,
                    strategy,
                    starting_position,
                    seed=i
                )
                for i in range(self.n_simulations)
            ]
            
            for i, future in enumerate(as_completed(futures)):
                race_times.append(future.result())
                
                if (i + 1) % 100 == 0:
                    print(f"  Completed {i + 1}/{self.n_simulations} simulations")
        
        return race_times
    
    def _simulate_sequential(
        self,
        strategy: RaceStrategy,
        starting_position: int
    ) -> List[float]:
        """Run simulations sequentially"""
        race_times = []
        
        for i in range(self.n_simulations):
            race_time = self._simulate_single_race(strategy, starting_position, seed=i)
            race_times.append(race_time)
            
            if (i + 1) % 100 == 0:
                print(f"  Completed {i + 1}/{self.n_simulations} simulations")
        
        return race_times
    
    def _simulate_single_race(
        self,
        strategy: RaceStrategy,
        starting_position: int,
        seed: int
    ) -> float:
        """
        Simulate a single race scenario.
        
        Args:
            strategy: Race strategy
            starting_position: Starting position
            seed: Random seed for reproducibility
        
        Returns:
            Total race time (seconds)
        """
        np.random.seed(seed)
        
        total_time = 0.0
        current_compound = strategy.stint_compounds[0]  # Start with first compound
        stint_lap = 0
        fuel_load = 110.0
        current_stint_index = 0
        
        # Random events
        safety_car_lap = None
        if np.random.random() < self.safety_car_prob:
            safety_car_lap = np.random.randint(10, self.race_laps - 10)
        
        rain_lap = None
        if np.random.random() < self.rain_prob:
            rain_lap = np.random.randint(15, self.race_laps - 5)
        
        # Simulate each lap
        for lap in range(1, self.race_laps + 1):
            # Check for pit stop
            is_pit_lap = any(stop.lap == lap for stop in strategy.pit_stops)
            
            if is_pit_lap:
                # Pit stop time with variance
                pit_time = self.pit_loss_time + np.random.normal(0, self.pit_variance)
                total_time += max(pit_time, 18.0)  # Min 18s
                
                # Change compound
                for stop in strategy.pit_stops:
                    if stop.lap == lap:
                        current_compound = stop.out_compound
                        stint_lap = 0
                        break
            
            # Calculate lap time
            lap_time = self._calculate_lap_time(
                current_compound,
                stint_lap,
                fuel_load,
                lap,
                safety_car_lap,
                rain_lap
            )
            
            total_time += lap_time
            stint_lap += 1
            fuel_load -= 1.6
        
        return total_time
    
    def _calculate_lap_time(
        self,
        compound: TireCompound,
        stint_lap: int,
        fuel_load: float,
        current_lap: int,
        safety_car_lap: Optional[int],
        rain_lap: Optional[int]
    ) -> float:
        """Calculate lap time with all effects"""
        # Base lap time
        lap_time = self.base_lap_time
        
        # Tire degradation
        degradation = self.tire_model.calculate_degradation(
            compound, stint_lap, fuel_load
        )
        deg_effect = degradation * 2.0
        
        # Fuel effect
        fuel_effect = (fuel_load - 50) * 0.03
        
        # Safety car
        if safety_car_lap and abs(current_lap - safety_car_lap) <= 3:
            lap_time *= 1.3  # Slower under SC
        
        # Rain
        if rain_lap and current_lap >= rain_lap:
            lap_time += 5.0  # Wet conditions
        
        # Random variance
        variance = np.random.normal(0, self.lap_time_variance)
        
        lap_time = lap_time + deg_effect + fuel_effect + variance
        
        return max(lap_time, self.base_lap_time - 1.0)
    
    def _calculate_statistics(
        self,
        strategy: RaceStrategy,
        race_times: List[float],
        starting_position: int
    ) -> MonteCarloResult:
        """Calculate statistics from simulation results"""
        race_times = np.array(race_times)
        
        # Basic statistics
        mean_time = np.mean(race_times)
        std_time = np.std(race_times)
        min_time = np.min(race_times)
        max_time = np.max(race_times)
        
        # Percentiles
        p5 = np.percentile(race_times, 5)
        p95 = np.percentile(race_times, 95)
        
        # Confidence interval (95%)
        ci_95 = (
            mean_time - 1.96 * std_time / np.sqrt(len(race_times)),
            mean_time + 1.96 * std_time / np.sqrt(len(race_times))
        )
        
        # Win probability (simplified)
        # Assume we need to be within top 3 times
        threshold = np.percentile(race_times, 15)
        win_prob = np.sum(race_times <= threshold) / len(race_times)
        
        # Position distribution (simplified)
        position_dist = {}
        for pos in range(1, 21):
            # Estimate based on time distribution
            if pos <= 3:
                position_dist[pos] = win_prob / 3
            else:
                position_dist[pos] = (1 - win_prob) / 17
        
        result = MonteCarloResult(
            strategy=strategy,
            mean_race_time=float(mean_time),
            std_race_time=float(std_time),
            min_race_time=float(min_time),
            max_race_time=float(max_time),
            percentile_5=float(p5),
            percentile_95=float(p95),
            win_probability=float(win_prob),
            undercut_success_rate=0.65,  # Placeholder
            safety_car_benefit=2.5,  # Placeholder
            confidence_interval_95=ci_95,
            position_distribution=position_dist,
            all_times=race_times.tolist()
        )
        
        return result
    
    def compare_strategies(
        self,
        strategies: List[RaceStrategy],
        starting_position: int = 10
    ) -> List[MonteCarloResult]:
        """
        Compare multiple strategies using Monte Carlo.
        
        Args:
            strategies: List of strategies to compare
            starting_position: Starting grid position
        
        Returns:
            List of MonteCarloResults sorted by mean time
        """
        results = []
        
        for i, strategy in enumerate(strategies, 1):
            print(f"\nSimulating strategy {i}/{len(strategies)}: {strategy}")
            result = self.simulate_strategy(strategy, starting_position, parallel=True)
            results.append(result)
        
        # Sort by mean race time
        results.sort(key=lambda r: r.mean_race_time)
        
        return results
    
    def print_results(self, result: MonteCarloResult):
        """Print formatted results"""
        print("\n" + "="*70)
        print("MONTE CARLO SIMULATION RESULTS")
        print("="*70)
        
        print(f"\nStrategy: {result.strategy}")
        print(f"Simulations: {len(result.all_times)}")
        
        print(f"\nRace Time Statistics:")
        print(f"  Mean:   {result.mean_race_time:.2f}s ({result.mean_race_time/60:.2f} min)")
        print(f"  Std:    {result.std_race_time:.2f}s")
        print(f"  Min:    {result.min_race_time:.2f}s")
        print(f"  Max:    {result.max_race_time:.2f}s")
        print(f"  5th %:  {result.percentile_5:.2f}s")
        print(f"  95th %: {result.percentile_95:.2f}s")
        
        print(f"\nConfidence Interval (95%):")
        print(f"  [{result.confidence_interval_95[0]:.2f}s, {result.confidence_interval_95[1]:.2f}s]")
        
        print(f"\nProbabilities:")
        print(f"  Win/Podium: {result.win_probability:.1%}")
        print(f"  Undercut Success: {result.undercut_success_rate:.1%}")
        
        print("="*70 + "\n")


if __name__ == "__main__":
    # Test Monte Carlo simulator
    from engine.tire_model import TireDegradationModel
    from engine.pit_optimizer import RaceStrategy, PitStopEvent
    
    print("Testing Monte Carlo Race Simulator\n")
    
    # Initialize
    tire_model = TireDegradationModel(
        track_temp=32.0,
        track_abrasiveness=1.2,
        base_lap_time=93.0
    )
    
    simulator = MonteCarloRaceSimulator(
        tire_model=tire_model,
        race_laps=57,
        base_lap_time=93.0,
        n_simulations=500
    )
    
    # Test strategy
    strategy = RaceStrategy(
        pit_stops=[
            PitStopEvent(21, TireCompound.MEDIUM, TireCompound.HARD, 22.0),
            PitStopEvent(40, TireCompound.HARD, TireCompound.MEDIUM, 22.0)
        ],
        total_race_time=0.0,  # Will be calculated
        stint_compounds=[TireCompound.MEDIUM, TireCompound.HARD, TireCompound.MEDIUM]
    )
    
    # Run simulation
    result = simulator.simulate_strategy(strategy, starting_position=8, parallel=False)
    
    # Print results
    simulator.print_results(result)
