"""
F1 Race Strategy Simulation Engine

This is the main simulation engine that integrates all models to simulate
complete race strategies and provide real-time strategic recommendations.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from engine.tire_model import TireCompound, TireDegradationModel
from engine.pit_optimizer import PitStrategyOptimizer, RaceStrategy, PitStopEvent
from engine.fuel_model import FuelModel, ERSModel
from engine.weather_model import WeatherModel, WeatherState, WeatherCondition, TrackCondition
from engine.opponent_model import OpponentPaceModel, Driver, OpponentState, TeamTier


@dataclass
class RaceConfig:
    """Race configuration parameters"""
    track_name: str
    race_laps: int
    base_lap_time: float
    track_temp: float = 30.0
    track_abrasiveness: float = 1.0
    pit_loss_time: float = 22.0
    overtaking_difficulty: str = "MEDIUM"
    drs_zones: int = 2
    initial_fuel: float = 110.0
    fuel_per_lap: float = 1.6


@dataclass
class SimulationResult:
    """Complete simulation result"""
    strategy: RaceStrategy
    total_race_time: float
    final_position: int
    lap_by_lap_data: List[Dict]
    fuel_remaining: float
    tire_states: List[Dict]
    weather_events: List[Dict]
    overtakes: int
    risk_events: List[str]
    
    def summary(self) -> str:
        """Generate human-readable summary"""
        return (
            f"Race Result Summary\n"
            f"{'='*50}\n"
            f"Strategy: {self.strategy}\n"
            f"Total Time: {self.total_race_time:.1f}s ({self.total_race_time/60:.1f} min)\n"
            f"Final Position: P{self.final_position}\n"
            f"Overtakes: {self.overtakes}\n"
            f"Fuel Remaining: {self.fuel_remaining:.1f} kg\n"
            f"Risk Events: {len(self.risk_events)}\n"
        )


class F1SimulationEngine:
    """
    Main F1 race strategy simulation engine.
    
    Integrates all sub-models to provide:
    - Complete race simulation
    - Real-time strategy recommendations
    - What-if scenario analysis
    - Risk assessment
    """
    
    def __init__(self, race_config: RaceConfig):
        """
        Initialize simulation engine with race configuration.
        
        Args:
            race_config: Race configuration parameters
        """
        self.config = race_config
        
        # Initialize all sub-models
        self.tire_model = TireDegradationModel(
            track_temp=race_config.track_temp,
            track_abrasiveness=race_config.track_abrasiveness,
            base_lap_time=race_config.base_lap_time
        )
        
        self.pit_optimizer = PitStrategyOptimizer(
            tire_model=self.tire_model,
            race_laps=race_config.race_laps,
            track_name=race_config.track_name,
            pit_loss_time=race_config.pit_loss_time
        )
        
        self.fuel_model = FuelModel(
            race_laps=race_config.race_laps,
            base_lap_time=race_config.base_lap_time,
            initial_fuel=race_config.initial_fuel
        )
        
        self.weather_model = WeatherModel(
            initial_weather=WeatherState(
                condition=WeatherCondition.DRY,
                track_condition=TrackCondition.DRY,
                track_temp=race_config.track_temp,
                air_temp=25.0,
                humidity=60.0,
                rain_intensity=0.0,
                wind_speed=10.0
            )
        )
        
        self.opponent_model = OpponentPaceModel(
            track_overtaking_difficulty=race_config.overtaking_difficulty,
            drs_zones=race_config.drs_zones
        )
        
        self.ers_model = ERSModel()
        
    def simulate_race(
        self,
        strategy: RaceStrategy,
        starting_position: int = 10,
        opponents: Optional[List[OpponentState]] = None
    ) -> SimulationResult:
        """
        Simulate a complete race with given strategy.
        
        Args:
            strategy: Race strategy to simulate
            starting_position: Starting grid position
            opponents: List of opponent states (optional)
            
        Returns:
            Complete simulation result
        """
        print(f"\nSimulating race: {self.config.track_name}")
        print(f"Strategy: {strategy}")
        
        # Initialize race state
        current_lap = 1
        current_position = starting_position
        current_compound = strategy.stint_compounds[0]
        tire_age = 0
        fuel_load = self.config.initial_fuel
        stint_index = 0
        
        lap_by_lap_data = []
        tire_states = []
        weather_events = []
        risk_events = []
        overtakes = 0
        
        total_time = 0.0
        
        # Simulate each lap
        for lap in range(1, self.config.race_laps + 1):
            # Check for pit stop
            pit_this_lap = False
            if stint_index < len(strategy.pit_stops):
                if lap == strategy.pit_stops[stint_index].lap:
                    pit_this_lap = True
                    
                    # Pit stop
                    total_time += self.config.pit_loss_time
                    current_compound = strategy.pit_stops[stint_index].out_compound
                    tire_age = 0
                    stint_index += 1
                    
                    # Record pit event
                    lap_by_lap_data.append({
                        'lap': lap,
                        'event': 'PIT_STOP',
                        'compound': current_compound.value,
                        'time_loss': self.config.pit_loss_time
                    })
            
            if not pit_this_lap:
                tire_age += 1
                
                # Calculate lap time with all effects
                base_lap_time = self.tire_model.predict_lap_time(
                    current_compound,
                    tire_age,
                    fuel_load
                )
                
                # Add fuel effect
                lap_time = self.fuel_model.predict_lap_time_with_fuel(
                    base_lap_time,
                    fuel_load,
                    "NORMAL"
                )
                
                # Add weather effect
                weather_delta = self.weather_model.calculate_weather_lap_time_delta(
                    self.weather_model.current_weather,
                    "SLICK"
                )
                lap_time += weather_delta
                
                # Add traffic effect
                traffic_delta = self.opponent_model.calculate_traffic_impact(
                    current_position
                )
                lap_time += traffic_delta
                
                # Random variation (driver errors, etc.)
                lap_time += np.random.normal(0, 0.15)
                
                total_time += lap_time
                
                # Consume fuel
                fuel_load = max(0, fuel_load - self.config.fuel_per_lap)
                
                # Record lap data
                tire_deg = self.tire_model.calculate_degradation(
                    current_compound,
                    tire_age,
                    fuel_load
                )
                
                lap_by_lap_data.append({
                    'lap': lap,
                    'lap_time': lap_time,
                    'compound': current_compound.value,
                    'tire_age': tire_age,
                    'tire_degradation': tire_deg,
                    'fuel_load': fuel_load,
                    'position': current_position,
                    'total_time': total_time
                })
                
                tire_states.append({
                    'lap': lap,
                    'compound': current_compound.value,
                    'age': tire_age,
                    'degradation': tire_deg
                })
                
                # Check for risk events
                if tire_deg > 0.9:
                    risk_events.append(f"Lap {lap}: Critical tire degradation ({tire_deg:.1%})")
                
                if fuel_load < 5.0:
                    risk_events.append(f"Lap {lap}: Low fuel warning ({fuel_load:.1f} kg)")
        
        # Calculate final position (simplified)
        final_position = max(1, starting_position - (overtakes // 2))
        
        result = SimulationResult(
            strategy=strategy,
            total_race_time=total_time,
            final_position=final_position,
            lap_by_lap_data=lap_by_lap_data,
            fuel_remaining=fuel_load,
            tire_states=tire_states,
            weather_events=weather_events,
            overtakes=overtakes,
            risk_events=risk_events
        )
        
        return result
    
    def optimize_strategy(
        self,
        max_stops: int = 3,
        starting_position: int = 10
    ) -> List[SimulationResult]:
        """
        Find and simulate optimal strategies.
        
        Args:
            max_stops: Maximum pit stops to consider
            starting_position: Starting grid position
            
        Returns:
            List of simulation results for top strategies
        """
        print(f"\n{'='*60}")
        print(f"OPTIMIZING STRATEGY: {self.config.track_name}")
        print(f"{'='*60}")
        
        # Get top strategies from optimizer
        top_strategies = self.pit_optimizer.optimize_strategy(
            max_stops=max_stops,
            top_n=5
        )
        
        # Simulate each strategy
        results = []
        for i, strategy in enumerate(top_strategies, 1):
            print(f"\nSimulating Strategy {i}/5...")
            result = self.simulate_race(strategy, starting_position)
            results.append(result)
        
        # Sort by total race time
        results.sort(key=lambda x: x.total_race_time)
        
        return results
    
    def real_time_recommendation(
        self,
        current_lap: int,
        current_position: int,
        current_compound: TireCompound,
        tire_age: int,
        fuel_load: float,
        gap_ahead: float,
        gap_behind: float
    ) -> Dict[str, any]:
        """
        Provide real-time strategy recommendation during a race.
        
        Args:
            current_lap: Current race lap
            current_position: Current position
            current_compound: Current tire compound
            tire_age: Current tire age (laps)
            fuel_load: Current fuel load (kg)
            gap_ahead: Gap to car ahead (seconds)
            gap_behind: Gap to car behind (seconds)
            
        Returns:
            Dictionary with strategic recommendations
        """
        remaining_laps = self.config.race_laps - current_lap
        
        # Tire degradation assessment
        tire_deg = self.tire_model.calculate_degradation(
            current_compound,
            tire_age,
            fuel_load
        )
        
        # Optimal pit window
        pit_window = self.tire_model.optimal_pit_window(current_compound)
        
        # Should pit?
        should_pit = tire_age >= pit_window[0] and tire_age <= pit_window[1]
        
        # Fuel check
        fuel_analysis = self.fuel_model.calculate_fuel_saving_benefit(
            current_lap,
            remaining_laps,
            fuel_load
        )
        
        # Weather forecast
        weather_forecast = self.weather_model.predict_weather_evolution(
            remaining_laps,
            rain_probability=0.2
        )
        
        # Compile recommendation
        recommendation = {
            'current_lap': current_lap,
            'tire_degradation': tire_deg,
            'tire_age': tire_age,
            'pit_window': pit_window,
            'should_pit': should_pit,
            'fuel_status': fuel_analysis['recommendation'],
            'must_save_fuel': fuel_analysis['must_save_fuel'],
            'weather_outlook': weather_forecast[0].condition.value if weather_forecast else 'DRY',
            'strategic_action': self._determine_action(
                should_pit, tire_deg, fuel_analysis, gap_ahead, gap_behind
            )
        }
        
        return recommendation
    
    def _determine_action(
        self,
        should_pit: bool,
        tire_deg: float,
        fuel_analysis: Dict,
        gap_ahead: float,
        gap_behind: float
    ) -> str:
        """Determine strategic action based on current state."""
        if tire_deg > 0.95:
            return "⚠️ PIT IMMEDIATELY - Critical tire degradation"
        elif fuel_analysis['must_save_fuel']:
            return "⚠️ FUEL SAVE MODE - Switch to fuel-saving"
        elif should_pit and gap_behind > 20.0:
            return "✅ PIT NOW - Safe window, good gap behind"
        elif should_pit and gap_ahead < 3.0:
            return "🎯 UNDERCUT OPPORTUNITY - Pit to undercut car ahead"
        elif should_pit:
            return "⏳ CONSIDER PITTING - In optimal window"
        elif tire_deg < 0.5:
            return "✅ STAY OUT - Tires still good, push"
        else:
            return "📊 MONITOR - Continue current strategy"
    
    def compare_strategies(
        self,
        strategies: List[RaceStrategy],
        starting_position: int = 10
    ) -> None:
        """
        Compare multiple strategies side-by-side.
        
        Args:
            strategies: List of strategies to compare
            starting_position: Starting grid position
        """
        print(f"\n{'='*60}")
        print("STRATEGY COMPARISON")
        print(f"{'='*60}\n")
        
        results = []
        for strategy in strategies:
            result = self.simulate_race(strategy, starting_position)
            results.append(result)
        
        # Print comparison table
        print(f"{'Strategy':<30} {'Time':<12} {'Pos':<6} {'Risk':<10}")
        print("-" * 60)
        
        for result in results:
            strategy_str = str(result.strategy)[:28]
            time_str = f"{result.total_race_time:.1f}s"
            pos_str = f"P{result.final_position}"
            risk_str = f"{len(result.risk_events)} events"
            
            print(f"{strategy_str:<30} {time_str:<12} {pos_str:<6} {risk_str:<10}")
        
        # Highlight best strategy
        best = min(results, key=lambda x: x.total_race_time)
        print(f"\n✅ OPTIMAL STRATEGY: {best.strategy}")
        print(f"   Expected time: {best.total_race_time:.1f}s")


if __name__ == "__main__":
    # Example usage - Bahrain GP simulation
    print("="*70)
    print("F1 RACE STRATEGY SIMULATION ENGINE")
    print("="*70)
    
    # Configure race
    bahrain_config = RaceConfig(
        track_name="Bahrain International Circuit",
        race_laps=57,
        base_lap_time=93.0,  # ~1:33.0
        track_temp=32.0,
        track_abrasiveness=1.1,
        pit_loss_time=22.0,
        overtaking_difficulty="EASY",
        drs_zones=2,
        initial_fuel=110.0,
        fuel_per_lap=1.6
    )
    
    # Initialize engine
    engine = F1SimulationEngine(bahrain_config)
    
    # Optimize and simulate strategies
    results = engine.optimize_strategy(max_stops=2, starting_position=8)
    
    # Print results
    print(f"\n{'='*70}")
    print("SIMULATION RESULTS")
    print(f"{'='*70}\n")
    
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. {result.summary()}")
        
        # Show sample laps
        print("\nSample Lap Times:")
        for lap_data in result.lap_by_lap_data[::10]:  # Every 10th lap
            if 'lap_time' in lap_data:
                print(f"  Lap {lap_data['lap']:2d}: {lap_data['lap_time']:.3f}s "
                      f"({lap_data['compound']}, Age: {lap_data['tire_age']})")
    
    # Real-time recommendation example
    print(f"\n{'='*70}")
    print("REAL-TIME STRATEGY RECOMMENDATION (Lap 25)")
    print(f"{'='*70}\n")
    
    recommendation = engine.real_time_recommendation(
        current_lap=25,
        current_position=6,
        current_compound=TireCompound.MEDIUM,
        tire_age=18,
        fuel_load=60.0,
        gap_ahead=2.5,
        gap_behind=4.8
    )
    
    print(f"Tire Degradation: {recommendation['tire_degradation']:.1%}")
    print(f"Tire Age: {recommendation['tire_age']} laps")
    print(f"Optimal Pit Window: Laps {recommendation['pit_window'][0]}-{recommendation['pit_window'][1]}")
    print(f"Fuel Status: {recommendation['fuel_status']}")
    print(f"\n🎯 RECOMMENDATION: {recommendation['strategic_action']}")
