"""
F1 Data Loaders

This module provides data loading functionality for historical F1 data
using FastF1 and other data sources.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

try:
    import fastf1
    FASTF1_AVAILABLE = True
except ImportError:
    FASTF1_AVAILABLE = False
    print("Warning: FastF1 not installed. Historical data loading will be limited.")


class F1DataLoader:
    """
    Loads historical F1 race data from various sources.
    
    Primary source: FastF1 (official F1 timing data)
    Fallback: Manual data files
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialize data loader.
        
        Args:
            cache_dir: Directory for caching downloaded data
        """
        self.cache_dir = cache_dir
        
        if FASTF1_AVAILABLE:
            fastf1.Cache.enable_cache(cache_dir)
    
    def load_race_session(
        self,
        year: int,
        race: str,
        session: str = 'R'
    ) -> Optional[object]:
        """
        Load a race session using FastF1.
        
        Args:
            year: Race year (e.g., 2024)
            race: Race name or round number (e.g., 'Bahrain' or 1)
            session: Session type ('FP1', 'FP2', 'FP3', 'Q', 'R')
            
        Returns:
            FastF1 session object or None if unavailable
        """
        if not FASTF1_AVAILABLE:
            print("FastF1 not available. Cannot load session.")
            return None
        
        try:
            session_obj = fastf1.get_session(year, race, session)
            session_obj.load()
            print(f"✅ Loaded {year} {race} - {session}")
            return session_obj
        except Exception as e:
            print(f"❌ Error loading session: {e}")
            return None
    
    def extract_lap_data(
        self,
        session: object,
        driver: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extract lap-by-lap data from a session.
        
        Args:
            session: FastF1 session object
            driver: Driver code (e.g., 'VER', 'HAM') or None for all drivers
            
        Returns:
            DataFrame with lap data
        """
        if session is None:
            return pd.DataFrame()
        
        try:
            laps = session.laps
            
            if driver:
                laps = laps.pick_driver(driver)
            
            # Extract relevant columns
            lap_data = pd.DataFrame({
                'lap_number': laps['LapNumber'],
                'driver': laps['Driver'],
                'team': laps['Team'],
                'lap_time': laps['LapTime'].dt.total_seconds(),
                'sector1_time': laps['Sector1Time'].dt.total_seconds(),
                'sector2_time': laps['Sector2Time'].dt.total_seconds(),
                'sector3_time': laps['Sector3Time'].dt.total_seconds(),
                'compound': laps['Compound'],
                'tire_life': laps['TyreLife'],
                'stint': laps['Stint'],
                'is_personal_best': laps['IsPersonalBest'],
            })
            
            return lap_data.dropna(subset=['lap_time'])
        
        except Exception as e:
            print(f"Error extracting lap data: {e}")
            return pd.DataFrame()
    
    def extract_pit_stops(
        self,
        session: object
    ) -> pd.DataFrame:
        """
        Extract pit stop data from a session.
        
        Args:
            session: FastF1 session object
            
        Returns:
            DataFrame with pit stop data
        """
        if session is None:
            return pd.DataFrame()
        
        try:
            laps = session.laps
            
            # Identify pit laps (where stint changes)
            pit_laps = laps[laps['PitInTime'].notna()].copy()
            
            pit_data = pd.DataFrame({
                'driver': pit_laps['Driver'],
                'lap': pit_laps['LapNumber'],
                'pit_in_time': pit_laps['PitInTime'],
                'pit_out_time': pit_laps['PitOutTime'],
                'pit_duration': (pit_laps['PitOutTime'] - pit_laps['PitInTime']).dt.total_seconds(),
                'compound_before': pit_laps['Compound'],
                'tire_life_before': pit_laps['TyreLife'],
            })
            
            return pit_data
        
        except Exception as e:
            print(f"Error extracting pit stops: {e}")
            return pd.DataFrame()
    
    def extract_telemetry(
        self,
        session: object,
        driver: str,
        lap: int
    ) -> pd.DataFrame:
        """
        Extract detailed telemetry for a specific lap.
        
        Args:
            session: FastF1 session object
            driver: Driver code
            lap: Lap number
            
        Returns:
            DataFrame with telemetry data (speed, throttle, brake, etc.)
        """
        if session is None:
            return pd.DataFrame()
        
        try:
            lap_obj = session.laps.pick_driver(driver).pick_lap(lap)
            telemetry = lap_obj.get_telemetry()
            
            return pd.DataFrame({
                'time': telemetry['Time'].dt.total_seconds(),
                'speed': telemetry['Speed'],
                'throttle': telemetry['Throttle'],
                'brake': telemetry['Brake'],
                'gear': telemetry['nGear'],
                'rpm': telemetry['RPM'],
                'drs': telemetry['DRS'],
            })
        
        except Exception as e:
            print(f"Error extracting telemetry: {e}")
            return pd.DataFrame()
    
    def get_race_results(
        self,
        session: object
    ) -> pd.DataFrame:
        """
        Get final race results.
        
        Args:
            session: FastF1 session object
            
        Returns:
            DataFrame with race results
        """
        if session is None:
            return pd.DataFrame()
        
        try:
            results = session.results
            
            return pd.DataFrame({
                'position': results['Position'],
                'driver': results['Abbreviation'],
                'team': results['TeamName'],
                'points': results['Points'],
                'status': results['Status'],
                'time': results['Time'],
            })
        
        except Exception as e:
            print(f"Error getting race results: {e}")
            return pd.DataFrame()
    
    def load_track_info(
        self,
        track_name: str
    ) -> Dict[str, any]:
        """
        Load track information and characteristics.
        
        Args:
            track_name: Name of the track
            
        Returns:
            Dictionary with track information
        """
        # Predefined track database
        track_database = {
            'Bahrain': {
                'full_name': 'Bahrain International Circuit',
                'length_km': 5.412,
                'laps': 57,
                'corners': 15,
                'drs_zones': 2,
                'overtaking_difficulty': 'EASY',
                'track_abrasiveness': 1.2,
                'typical_temp': 30.0,
                'lap_record': 91.5,
            },
            'Saudi Arabia': {
                'full_name': 'Jeddah Corniche Circuit',
                'length_km': 6.174,
                'laps': 50,
                'corners': 27,
                'drs_zones': 3,
                'overtaking_difficulty': 'MEDIUM',
                'track_abrasiveness': 0.9,
                'typical_temp': 28.0,
                'lap_record': 90.7,
            },
            'Monaco': {
                'full_name': 'Circuit de Monaco',
                'length_km': 3.337,
                'laps': 78,
                'corners': 19,
                'drs_zones': 1,
                'overtaking_difficulty': 'HARD',
                'track_abrasiveness': 0.8,
                'typical_temp': 22.0,
                'lap_record': 70.2,
            },
            'Silverstone': {
                'full_name': 'Silverstone Circuit',
                'length_km': 5.891,
                'laps': 52,
                'corners': 18,
                'drs_zones': 2,
                'overtaking_difficulty': 'MEDIUM',
                'track_abrasiveness': 1.1,
                'typical_temp': 20.0,
                'lap_record': 87.1,
            },
            'Monza': {
                'full_name': 'Autodromo Nazionale di Monza',
                'length_km': 5.793,
                'laps': 53,
                'corners': 11,
                'drs_zones': 2,
                'overtaking_difficulty': 'EASY',
                'track_abrasiveness': 0.9,
                'typical_temp': 26.0,
                'lap_record': 81.0,
            },
        }
        
        return track_database.get(track_name, {
            'full_name': track_name,
            'length_km': 5.0,
            'laps': 50,
            'corners': 15,
            'drs_zones': 2,
            'overtaking_difficulty': 'MEDIUM',
            'track_abrasiveness': 1.0,
            'typical_temp': 25.0,
            'lap_record': 90.0,
        })


class HistoricalDataAnalyzer:
    """
    Analyzes historical race data to extract patterns and insights.
    """
    
    def __init__(self, loader: F1DataLoader):
        """
        Initialize analyzer with data loader.
        
        Args:
            loader: F1DataLoader instance
        """
        self.loader = loader
    
    def analyze_tire_degradation(
        self,
        lap_data: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Analyze tire degradation patterns from historical data.
        
        Args:
            lap_data: DataFrame with lap data
            
        Returns:
            Dictionary with degradation analysis
        """
        if lap_data.empty:
            return {}
        
        # Group by compound and tire life
        degradation_by_compound = {}
        
        for compound in lap_data['compound'].unique():
            if pd.isna(compound):
                continue
            
            compound_data = lap_data[lap_data['compound'] == compound].copy()
            
            # Calculate average lap time by tire life
            avg_by_life = compound_data.groupby('tire_life')['lap_time'].mean()
            
            # Calculate degradation rate (seconds per lap)
            if len(avg_by_life) > 1:
                deg_rate = (avg_by_life.iloc[-1] - avg_by_life.iloc[0]) / len(avg_by_life)
            else:
                deg_rate = 0.0
            
            degradation_by_compound[compound] = {
                'avg_lap_time': compound_data['lap_time'].mean(),
                'degradation_rate': deg_rate,
                'max_stint_length': compound_data['tire_life'].max(),
                'optimal_window': (
                    int(avg_by_life.idxmin()) if len(avg_by_life) > 0 else 0,
                    int(len(avg_by_life) * 0.7)
                )
            }
        
        return degradation_by_compound
    
    def analyze_pit_strategy(
        self,
        lap_data: pd.DataFrame,
        pit_data: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Analyze pit stop strategies from historical data.
        
        Args:
            lap_data: DataFrame with lap data
            pit_data: DataFrame with pit stop data
            
        Returns:
            Dictionary with pit strategy analysis
        """
        if pit_data.empty:
            return {}
        
        analysis = {
            'avg_pit_duration': pit_data['pit_duration'].mean(),
            'pit_lap_distribution': pit_data['lap'].describe().to_dict(),
            'most_common_strategy': self._identify_common_strategy(lap_data),
        }
        
        return analysis
    
    def _identify_common_strategy(
        self,
        lap_data: pd.DataFrame
    ) -> str:
        """Identify most common pit strategy."""
        if lap_data.empty:
            return "Unknown"
        
        # Count number of stints per driver
        stints_per_driver = lap_data.groupby('driver')['stint'].max()
        
        # Most common number of stops (stints - 1)
        most_common_stops = stints_per_driver.mode().values[0] - 1 if len(stints_per_driver) > 0 else 1
        
        return f"{int(most_common_stops)}-stop"


if __name__ == "__main__":
    # Example usage
    print("="*60)
    print("F1 DATA LOADER DEMO")
    print("="*60)
    
    # Initialize loader
    loader = F1DataLoader(cache_dir="./cache")
    
    # Load track info
    print("\n=== Track Information ===")
    bahrain_info = loader.load_track_info('Bahrain')
    print(f"Track: {bahrain_info['full_name']}")
    print(f"Length: {bahrain_info['length_km']} km")
    print(f"Laps: {bahrain_info['laps']}")
    print(f"DRS Zones: {bahrain_info['drs_zones']}")
    print(f"Overtaking Difficulty: {bahrain_info['overtaking_difficulty']}")
    
    if FASTF1_AVAILABLE:
        print("\n=== Loading Historical Data ===")
        print("Attempting to load 2024 Bahrain GP...")
        
        # Note: This requires internet connection and may take time
        # Uncomment to actually load data:
        # session = loader.load_race_session(2024, 'Bahrain', 'R')
        # if session:
        #     lap_data = loader.extract_lap_data(session, driver='VER')
        #     print(f"Loaded {len(lap_data)} laps for VER")
        #     print(lap_data.head())
    else:
        print("\n⚠️ FastF1 not installed.")
        print("Install with: pip install fastf1")
        print("This enables historical data loading from F1 timing data.")
