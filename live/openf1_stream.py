"""
OpenF1 Live Telemetry Stream Integration

This module connects to OpenF1 API to stream real-time race telemetry
and update strategy predictions live during a race.
"""

import requests
import json
import time
import numpy as np
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import threading


@dataclass
class LivePosition:
    """Live position data for a driver"""
    driver_number: int
    driver_name: str
    position: int
    gap_to_leader: float
    interval: float
    last_lap_time: float


@dataclass
class LiveTelemetry:
    """Live telemetry data"""
    driver_number: int
    timestamp: datetime
    speed: float
    rpm: int
    gear: int
    throttle: float
    brake: bool
    drs: int


class OpenF1Client:
    """
    Client for OpenF1 API to fetch live race data.
    
    OpenF1 provides real-time F1 data including:
    - Car positions
    - Lap times
    - Tire data
    - Pit stops
    - Weather
    """
    
    BASE_URL = "https://api.openf1.org/v1"
    
    def __init__(self):
        """Initialize OpenF1 client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'F1-Strategy-Suite/1.0'
        })
    
    def get_live_session(self) -> Optional[Dict]:
        """
        Get current live session information.
        
        Returns:
            Dictionary with session info or None if no live session
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/sessions", params={
                'session_type': 'Race',
                'date_start': datetime.now().strftime('%Y-%m-%d')
            })
            
            if response.status_code == 200:
                sessions = response.json()
                if sessions:
                    return sessions[0]
            
            return None
        
        except Exception as e:
            print(f"Error fetching live session: {e}")
            return None
    
    def get_live_positions(self, session_key: int) -> List[LivePosition]:
        """
        Get live positions for all drivers.
        
        Args:
            session_key: Session identifier
            
        Returns:
            List of LivePosition objects
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/position", params={
                'session_key': session_key
            })
            
            if response.status_code == 200:
                data = response.json()
                
                positions = []
                for item in data:
                    positions.append(LivePosition(
                        driver_number=item.get('driver_number'),
                        driver_name=item.get('driver_name', 'Unknown'),
                        position=item.get('position', 0),
                        gap_to_leader=item.get('gap_to_leader', 0.0),
                        interval=item.get('interval', 0.0),
                        last_lap_time=item.get('last_lap_time', 0.0)
                    ))
                
                return positions
            
            return []
        
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
    
    def get_lap_data(
        self,
        session_key: int,
        driver_number: Optional[int] = None
    ) -> List[Dict]:
        """
        Get lap data for session.
        
        Args:
            session_key: Session identifier
            driver_number: Specific driver number (optional)
            
        Returns:
            List of lap data dictionaries
        """
        try:
            params = {'session_key': session_key}
            if driver_number:
                params['driver_number'] = driver_number
            
            response = self.session.get(f"{self.BASE_URL}/laps", params=params)
            
            if response.status_code == 200:
                return response.json()
            
            return []
        
        except Exception as e:
            print(f"Error fetching lap data: {e}")
            return []
    
    def get_pit_stops(self, session_key: int) -> List[Dict]:
        """
        Get pit stop data for session.
        
        Args:
            session_key: Session identifier
            
        Returns:
            List of pit stop dictionaries
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/pit", params={
                'session_key': session_key
            })
            
            if response.status_code == 200:
                return response.json()
            
            return []
        
        except Exception as e:
            print(f"Error fetching pit stops: {e}")
            return []
    
    def get_weather(self, session_key: int) -> Optional[Dict]:
        """
        Get weather data for session.
        
        Args:
            session_key: Session identifier
            
        Returns:
            Dictionary with weather data or None
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/weather", params={
                'session_key': session_key
            })
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[-1]  # Most recent weather
            
            return None
        
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def get_car_data(
        self,
        session_key: int,
        driver_number: int
    ) -> List[Dict]:
        """
        Get car telemetry data.
        
        Args:
            session_key: Session identifier
            driver_number: Driver number
            
        Returns:
            List of telemetry data points
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/car_data", params={
                'session_key': session_key,
                'driver_number': driver_number
            })
            
            if response.status_code == 200:
                return response.json()
            
            return []
        
        except Exception as e:
            print(f"Error fetching car data: {e}")
            return []


class LiveStrategyMonitor:
    """
    Monitors live race data and provides real-time strategy updates.
    """
    
    def __init__(
        self,
        openf1_client: OpenF1Client,
        update_callback: Optional[Callable] = None
    ):
        """
        Initialize live strategy monitor.
        
        Args:
            openf1_client: OpenF1 client instance
            update_callback: Callback function for updates
        """
        self.client = openf1_client
        self.update_callback = update_callback
        self.is_monitoring = False
        self.monitor_thread = None
        self.current_session = None
    
    def start_monitoring(self, session_key: int, interval: int = 5):
        """
        Start monitoring live race data.
        
        Args:
            session_key: Session to monitor
            interval: Update interval in seconds
        """
        if self.is_monitoring:
            print("Already monitoring")
            return
        
        self.current_session = session_key
        self.is_monitoring = True
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(session_key, interval),
            daemon=True
        )
        self.monitor_thread.start()
        
        print(f"✅ Started monitoring session {session_key}")
    
    def stop_monitoring(self):
        """Stop monitoring live data."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        print("⏹️ Stopped monitoring")
    
    def _monitor_loop(self, session_key: int, interval: int):
        """
        Main monitoring loop.
        
        Args:
            session_key: Session to monitor
            interval: Update interval in seconds
        """
        while self.is_monitoring:
            try:
                # Fetch live data
                positions = self.client.get_live_positions(session_key)
                lap_data = self.client.get_lap_data(session_key)
                pit_stops = self.client.get_pit_stops(session_key)
                weather = self.client.get_weather(session_key)
                
                # Compile update
                update = {
                    'timestamp': datetime.now(),
                    'positions': positions,
                    'lap_data': lap_data,
                    'pit_stops': pit_stops,
                    'weather': weather
                }
                
                # Call update callback
                if self.update_callback:
                    self.update_callback(update)
                
                # Wait for next update
                time.sleep(interval)
            
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(interval)
    
    def get_driver_status(
        self,
        session_key: int,
        driver_number: int
    ) -> Dict[str, any]:
        """
        Get comprehensive status for a specific driver.
        
        Args:
            session_key: Session identifier
            driver_number: Driver number
            
        Returns:
            Dictionary with driver status
        """
        # Get position data
        positions = self.client.get_live_positions(session_key)
        driver_position = next(
            (p for p in positions if p.driver_number == driver_number),
            None
        )
        
        # Get lap data
        laps = self.client.get_lap_data(session_key, driver_number)
        
        # Get pit stops
        pit_stops = self.client.get_pit_stops(session_key)
        driver_pits = [p for p in pit_stops if p.get('driver_number') == driver_number]
        
        # Compile status
        status = {
            'driver_number': driver_number,
            'position': driver_position.position if driver_position else None,
            'gap_to_leader': driver_position.gap_to_leader if driver_position else None,
            'last_lap_time': driver_position.last_lap_time if driver_position else None,
            'total_laps': len(laps),
            'pit_stops': len(driver_pits),
            'last_pit_lap': driver_pits[-1].get('lap_number') if driver_pits else None,
        }
        
        return status


class MockLiveDataGenerator:
    """
    Generates mock live data for testing when no live race is available.
    """
    
    def __init__(self, race_laps: int = 57):
        """
        Initialize mock data generator.
        
        Args:
            race_laps: Total race laps
        """
        self.race_laps = race_laps
        self.current_lap = 1
        self.drivers = self._initialize_drivers()
    
    def _initialize_drivers(self) -> List[Dict]:
        drivers = [
            # Red Bull Racing
            {'number':1,'name':'VER','team':'Red Bull','base_pace':90.0},
            {'number':22,'name':'TSU','team':'Red Bull','base_pace':90.4},
            
            # Mercedes-AMG
            {'number':63,'name':'RUS','team':'Mercedes','base_pace':90.1},
            {'number':87,'name':'ANT','team':'Mercedes','base_pace':90.2},
            
            # Ferrari
            {'number':16,'name':'LEC','team':'Ferrari','base_pace':90.2},
            {'number':44,'name':'HAM','team':'Ferrari','base_pace':90.3},
            
            # McLaren
            {'number':4,'name':'NOR','team':'McLaren','base_pace':90.3},
            {'number':81,'name':'PIA','team':'McLaren','base_pace':90.4},
            
            # Aston Martin
            {'number':14,'name':'ALO','team':'Aston Martin','base_pace':90.5},
            {'number':18,'name':'STR','team':'Aston Martin','base_pace':90.6},
            
            # Alpine
            {'number':10,'name':'GAS','team':'Alpine','base_pace':90.7},
            {'number':25,'name':'DOO','team':'Alpine','base_pace':90.8},
            
            # Williams
            {'number':23,'name':'ALB','team':'Williams','base_pace':90.8},
            {'number':43,'name':'COL','team':'Williams','base_pace':90.9},
            
            # RB (Visa Cash App RB)
            {'number':30,'name':'LAW','team':'RB','base_pace':91.0},
            {'number':6,'name':'HAD','team':'RB','base_pace':91.1},
            
            # Sauber (soon to become Audi)
            {'number':27,'name':'HUL','team':'Sauber','base_pace':91.2},
            {'number':24,'name':'ZHO','team':'Sauber','base_pace':91.3},
            
            # Haas
            {'number':87,'name':'BEA','team':'Haas','base_pace':91.4},
            {'number':31,'name':'OCO','team':'Haas','base_pace':91.5},
        ]
        
        for i, driver in enumerate(drivers):
            driver['position'] = i + 1
            driver['gap_to_leader'] = i * 2.5
            driver['tire_age'] = 0
            driver['compound'] = 'MEDIUM'
        
        return drivers
    
    def generate_lap_update(self) -> Dict[str, any]:
        """
        Base generator: ONLY produces dynamic data.
        The freeze logic lives in EnhancedMockDataGenerator.
        """

        # ✅ DO NOT increment beyond race_laps
        if self.current_lap < self.race_laps:
            self.current_lap += 1

        # ✅ Update driver data
        for driver in self.drivers:
            driver['tire_age'] += 1

            lap_time = driver['base_pace'] + (driver['tire_age'] * 0.05)
            lap_time += np.random.normal(0, 0.2)

            driver['last_lap_time'] = lap_time
            driver['gap_to_leader'] += np.random.uniform(-0.5, 0.5)

        # ✅ Recalculate positions
        self.drivers.sort(key=lambda x: x['gap_to_leader'])
        for i, driver in enumerate(self.drivers):
            driver['position'] = i + 1

        return {
            'lap': self.current_lap,
            'drivers': [d.copy() for d in self.drivers],
            'weather': {
                'track_temp': 32.0,
                'air_temp': 28.0,
                'humidity': 45,
                'rainfall': False
            },
            # ✅ base generator NEVER marks finished
            'race_finished': self.current_lap >= self.race_laps
        }

class EnhancedMockDataGenerator(MockLiveDataGenerator):
    """
    Extended mock generator with:
    - lap clamping
    - FULL state freeze
    - position-change tracking
    - safe restart
    """

    def __init__(self, race_laps=57, *args, **kwargs):
        super().__init__(race_laps=race_laps, *args, **kwargs)
        self.finished = False
        self.final_snapshot = None
        self.last_update = {}

    def generate_lap_update(self):
        # ✅ If race is already finished → always return frozen snapshot
        if self.finished:
            return self.final_snapshot

        # ✅ Pre-check: if next lap would exceed race limit, DO NOT CALL super()
        if self.current_lap >= self.race_laps:
            self.finished = True
            self.final_snapshot = {
                "lap": self.race_laps,
                "drivers": [d.copy() for d in self.drivers],
                "weather": {
                    "track_temp": 32.0,
                    "air_temp": 28.0,
                    "humidity": 45,
                    "rainfall": False
                },
                "race_finished": True,
                "position_changes": {n: {"change": 0, "trend": "same"} for n in self.last_update},
            }
            return self.final_snapshot

        # ✅ Only update if race is NOT finished
        update = super().generate_lap_update()

        # ✅ Position-change tracking
        current_positions = {d["name"]: d["position"] for d in update["drivers"]}
        position_changes = {}

        for name, pos in current_positions.items():
            if name in self.last_update:
                delta = self.last_update[name] - pos
                position_changes[name] = {
                    "change": delta,
                    "trend": "up" if delta > 0 else ("down" if delta < 0 else "same")
                }
            else:
                position_changes[name] = {"change": 0, "trend": "same"}

        self.last_update = current_positions
        update["position_changes"] = position_changes

        return update

    def reset(self):
        self.finished = False
        self.final_snapshot = None
        self.last_update = {}
        self.current_lap = 1

