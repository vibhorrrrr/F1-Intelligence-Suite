"""
Enhanced Mock Live Data Generator with Race Finish Logic

This module generates realistic race simulation data with proper race finish
handling, final classification, and restart capabilities.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import copy
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class DriverState:
    """Complete state for a single driver"""
    number: int
    name: str
    team: str
    position: int
    gap_to_leader: float
    interval: float
    last_lap_time: float
    best_lap_time: float
    tire_compound: str
    tire_age: int
    pit_stops: int
    total_race_time: float
    stint_history: List[Dict] = field(default_factory=list)
    lap_times: List[float] = field(default_factory=list)
    positions: List[int] = field(default_factory=list)


class EnhancedMockDataGenerator:
    """
    Professional-grade mock race data generator with:
    - Realistic tire degradation
    - Pit stop strategies
    - Position battles
    - Safety car events
    - Weather changes
    - Race finish logic
    - Restart capability
    """
    
    def __init__(self, race_laps: int = 57, track_name: str = "Bahrain"):
        """
        Initialize enhanced mock data generator.
        
        Args:
            race_laps: Total race laps
            track_name: Name of the circuit
        """
        self.race_laps = race_laps
        self.track_name = track_name
        self.current_lap = 1
        self.finished = False
        self.final_snapshot = None
        self.last_update = {}
        
        # Initialize drivers
        self.drivers = self._initialize_drivers()
        
        # Race state
        self.safety_car_active = False
        self.safety_car_laps_remaining = 0
        self.weather_condition = "DRY"
        self.track_temp = 32.0
        
        # Strategy tracking
        self.pit_strategies = self._initialize_strategies()
        
    def _initialize_drivers(self) -> List[DriverState]:
        """Initialize 20 drivers with realistic data"""
        driver_data = [
            {'number': 1, 'name': 'VER', 'team': 'Red Bull Racing', 'base_pace': 90.0},
            {'number': 16, 'name': 'LEC', 'team': 'Ferrari', 'base_pace': 90.2},
            {'number': 44, 'name': 'HAM', 'team': 'Mercedes', 'base_pace': 90.3},
            {'number': 4, 'name': 'NOR', 'team': 'McLaren', 'base_pace': 90.4},
            {'number': 11, 'name': 'PER', 'team': 'Red Bull Racing', 'base_pace': 90.5},
            {'number': 63, 'name': 'RUS', 'team': 'Mercedes', 'base_pace': 90.6},
            {'number': 55, 'name': 'SAI', 'team': 'Ferrari', 'base_pace': 90.7},
            {'number': 81, 'name': 'PIA', 'team': 'McLaren', 'base_pace': 90.8},
            {'number': 14, 'name': 'ALO', 'team': 'Aston Martin', 'base_pace': 91.0},
            {'number': 18, 'name': 'STR', 'team': 'Aston Martin', 'base_pace': 91.2},
            {'number': 10, 'name': 'GAS', 'team': 'Alpine', 'base_pace': 91.3},
            {'number': 31, 'name': 'OCO', 'team': 'Alpine', 'base_pace': 91.4},
            {'number': 23, 'name': 'ALB', 'team': 'Williams', 'base_pace': 91.5},
            {'number': 2, 'name': 'SAR', 'team': 'Williams', 'base_pace': 91.6},
            {'number': 27, 'name': 'HUL', 'team': 'Haas', 'base_pace': 91.7},
            {'number': 20, 'name': 'MAG', 'team': 'Haas', 'base_pace': 91.8},
            {'number': 22, 'name': 'TSU', 'team': 'RB', 'base_pace': 91.9},
            {'number': 3, 'name': 'RIC', 'team': 'RB', 'base_pace': 92.0},
            {'number': 24, 'name': 'ZHO', 'team': 'Kick Sauber', 'base_pace': 92.1},
            {'number': 77, 'name': 'BOT', 'team': 'Kick Sauber', 'base_pace': 92.2},
        ]
        
        drivers = []
        for i, data in enumerate(driver_data):
            driver = DriverState(
                number=data['number'],
                name=data['name'],
                team=data['team'],
                position=i + 1,
                gap_to_leader=i * 2.5 if i > 0 else 0.0,
                interval=2.5 if i > 0 else 0.0,
                last_lap_time=data['base_pace'],
                best_lap_time=data['base_pace'],
                tire_compound='MEDIUM',
                tire_age=0,
                pit_stops=0,
                total_race_time=0.0,
                stint_history=[],
                lap_times=[],
                positions=[]
            )
            drivers.append(driver)
        
        return drivers
    
    def _initialize_strategies(self) -> Dict[int, Dict]:
        """Initialize pit strategies for each driver"""
        strategies = {}
        
        for driver in self.drivers:
            # Vary strategies
            if driver.position <= 5:
                # Front runners: aggressive 2-stop
                strategies[driver.number] = {
                    'stops': 2,
                    'stop_laps': [18, 38],
                    'compounds': ['MEDIUM', 'HARD', 'MEDIUM']
                }
            elif driver.position <= 10:
                # Midfield: conservative 2-stop
                strategies[driver.number] = {
                    'stops': 2,
                    'stop_laps': [20, 40],
                    'compounds': ['MEDIUM', 'MEDIUM', 'HARD']
                }
            else:
                # Back markers: 1-stop gamble
                strategies[driver.number] = {
                    'stops': 1,
                    'stop_laps': [28],
                    'compounds': ['MEDIUM', 'HARD']
                }
        
        return strategies
    
    def generate_update(self) -> Dict:
        """
        Generate next race update.
        
        Returns:
            Dictionary with complete race state
        """
        # If race is finished, return final snapshot
        if self.finished:
            return self.final_snapshot
        
        # Generate lap update
        update = self._simulate_lap()
        
        # Check if race is finished
        if self.current_lap >= self.race_laps:
            update['lap'] = self.race_laps
            update['race_finished'] = True
            self.finished = True
            self.final_snapshot = copy.deepcopy(update)
        else:
            update['race_finished'] = False
            self.current_lap += 1
        
        self.last_update = update
        return update
    
    def _simulate_lap(self) -> Dict:
        """Simulate a single lap for all drivers"""
        
        # Check for safety car
        self._update_safety_car()
        
        # Simulate each driver
        for driver in self.drivers:
            # Calculate lap time
            lap_time = self._calculate_lap_time(driver)
            
            # Check for pit stop
            if self._should_pit(driver):
                lap_time += 22.0  # Pit loss
                self._execute_pit_stop(driver)
            
            # Update driver state
            driver.last_lap_time = lap_time
            driver.best_lap_time = min(driver.best_lap_time, lap_time)
            driver.total_race_time += lap_time
            driver.lap_times.append(lap_time)
            driver.tire_age += 1
        
        # Update positions
        self._update_positions()
        
        # Build update dictionary
        update = {
            'lap': self.current_lap,
            'total_laps': self.race_laps,
            'safety_car': self.safety_car_active,
            'weather': self.weather_condition,
            'track_temp': self.track_temp,
            'timestamp': datetime.now().isoformat(),
            'drivers': self._serialize_drivers(),
            'race_finished': False
        }
        
        return update
    
    def _calculate_lap_time(self, driver: DriverState) -> float:
        """Calculate realistic lap time with degradation"""
        base_pace = self._get_base_pace(driver.number)
        
        # Tire degradation effect
        deg_factor = self._get_degradation_factor(driver.tire_compound, driver.tire_age)
        
        # Safety car effect
        if self.safety_car_active:
            return base_pace * 1.3  # Slower under SC
        
        # Fuel effect (lighter as race progresses)
        fuel_effect = (1.0 - (self.current_lap / self.race_laps)) * 0.3
        
        # Random variance
        variance = np.random.normal(0, 0.15)
        
        lap_time = base_pace + deg_factor - fuel_effect + variance
        
        return max(lap_time, base_pace - 1.0)  # Cap improvement
    
    def _get_base_pace(self, driver_number: int) -> float:
        """Get base pace for driver"""
        for driver in self.drivers:
            if driver.number == driver_number:
                # Extract from lap_times or use initial
                if driver.lap_times:
                    return min(driver.lap_times)
                return driver.last_lap_time
        return 90.0
    
    def _get_degradation_factor(self, compound: str, age: int) -> float:
        """Calculate tire degradation time penalty"""
        deg_rates = {
            'SOFT': 0.08,
            'MEDIUM': 0.05,
            'HARD': 0.03
        }
        
        rate = deg_rates.get(compound, 0.05)
        
        # Exponential degradation with cliff
        if age < 15:
            return age * rate
        else:
            # Cliff effect
            return 15 * rate + (age - 15) * rate * 2.0
    
    def _should_pit(self, driver: DriverState) -> bool:
        """Determine if driver should pit this lap"""
        strategy = self.pit_strategies.get(driver.number, {})
        stop_laps = strategy.get('stop_laps', [])
        
        # Check if this is a planned pit lap
        if self.current_lap in stop_laps:
            # Only pit if haven't done this stop yet
            if driver.pit_stops < len(stop_laps):
                return True
        
        return False
    
    def _execute_pit_stop(self, driver: DriverState):
        """Execute pit stop for driver"""
        strategy = self.pit_strategies[driver.number]
        compounds = strategy['compounds']
        
        # Record stint
        driver.stint_history.append({
            'compound': driver.tire_compound,
            'laps': driver.tire_age,
            'end_lap': self.current_lap
        })
        
        # Change tires
        driver.pit_stops += 1
        driver.tire_age = 0
        
        if driver.pit_stops < len(compounds):
            driver.tire_compound = compounds[driver.pit_stops]
    
    def _update_positions(self):
        """Update driver positions based on race time"""
        # Sort by total race time
        self.drivers.sort(key=lambda d: d.total_race_time)
        
        # Update positions and gaps
        for i, driver in enumerate(self.drivers):
            driver.position = i + 1
            driver.positions.append(i + 1)
            
            if i == 0:
                driver.gap_to_leader = 0.0
                driver.interval = 0.0
            else:
                driver.gap_to_leader = driver.total_race_time - self.drivers[0].total_race_time
                driver.interval = driver.total_race_time - self.drivers[i-1].total_race_time
    
    def _update_safety_car(self):
        """Update safety car state"""
        if self.safety_car_active:
            self.safety_car_laps_remaining -= 1
            if self.safety_car_laps_remaining <= 0:
                self.safety_car_active = False
        else:
            # Random SC probability (5% per lap between laps 10-45)
            if 10 <= self.current_lap <= 45:
                if np.random.random() < 0.02:
                    self.safety_car_active = True
                    self.safety_car_laps_remaining = np.random.randint(3, 6)
    
    def _serialize_drivers(self) -> List[Dict]:
        """Convert driver states to dictionaries"""
        return [
            {
                'number': d.number,
                'name': d.name,
                'team': d.team,
                'position': d.position,
                'gap_to_leader': round(d.gap_to_leader, 3),
                'interval': round(d.interval, 3),
                'last_lap_time': round(d.last_lap_time, 3),
                'best_lap_time': round(d.best_lap_time, 3),
                'tire_compound': d.tire_compound,
                'tire_age': d.tire_age,
                'pit_stops': d.pit_stops,
                'total_race_time': round(d.total_race_time, 1),
                'stint_history': d.stint_history,
                'lap_times': d.lap_times[-10:],  # Last 10 laps
                'positions': d.positions
            }
            for d in self.drivers
        ]
    
    def reset(self):
        """Reset race to initial state"""
        self.current_lap = 1
        self.finished = False
        self.final_snapshot = None
        self.last_update = {}
        self.safety_car_active = False
        self.safety_car_laps_remaining = 0
        
        # Reinitialize drivers
        self.drivers = self._initialize_drivers()
        self.pit_strategies = self._initialize_strategies()
    
    def get_final_classification(self) -> Dict:
        """Get final race classification with detailed stats"""
        if not self.finished:
            return None
        
        classification = {
            'race_name': self.track_name,
            'total_laps': self.race_laps,
            'finishers': [],
            'fastest_lap': None,
            'most_overtakes': None
        }
        
        # Sort by final position
        sorted_drivers = sorted(self.drivers, key=lambda d: d.position)
        
        fastest_lap_time = float('inf')
        fastest_lap_driver = None
        
        for driver in sorted_drivers:
            classification['finishers'].append({
                'position': driver.position,
                'number': driver.number,
                'name': driver.name,
                'team': driver.team,
                'total_time': round(driver.total_race_time, 3),
                'gap': round(driver.gap_to_leader, 3),
                'best_lap': round(driver.best_lap_time, 3),
                'pit_stops': driver.pit_stops,
                'tire_strategy': [s['compound'] for s in driver.stint_history] + [driver.tire_compound]
            })
            
            if driver.best_lap_time < fastest_lap_time:
                fastest_lap_time = driver.best_lap_time
                fastest_lap_driver = driver.name
        
        classification['fastest_lap'] = {
            'driver': fastest_lap_driver,
            'time': round(fastest_lap_time, 3)
        }
        
        return classification


if __name__ == "__main__":
    # Test the generator
    print("Testing Enhanced Mock Data Generator\n")
    
    gen = EnhancedMockDataGenerator(race_laps=5)
    
    for lap in range(7):  # Test beyond race finish
        update = gen.generate_update()
        print(f"Lap {update['lap']}/{update['total_laps']}")
        print(f"Race Finished: {update['race_finished']}")
        print(f"Leader: {update['drivers'][0]['name']} - {update['drivers'][0]['total_race_time']:.1f}s")
        print(f"Safety Car: {update['safety_car']}")
        print()
    
    # Test reset
    print("\n--- RESET ---\n")
    gen.reset()
    update = gen.generate_update()
    print(f"After reset - Lap: {update['lap']}")
