"""
F1 Track Configurations Database

Pre-configured settings for all major F1 circuits.
"""

from engine.sim_engine import RaceConfig
from typing import Dict

# Complete F1 2024 Calendar Track Configurations
TRACK_DATABASE: Dict[str, RaceConfig] = {
    "Bahrain": RaceConfig(
        track_name="Bahrain International Circuit",
        race_laps=57,
        base_lap_time=93.0,
        track_temp=32.0,
        track_abrasiveness=1.2,
        pit_loss_time=22.0,
        overtaking_difficulty="EASY",
        drs_zones=2
    ),
    
    "Saudi Arabia": RaceConfig(
        track_name="Jeddah Corniche Circuit",
        race_laps=50,
        base_lap_time=90.0,
        track_temp=28.0,
        track_abrasiveness=0.9,
        pit_loss_time=23.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=3
    ),
    
    "Australia": RaceConfig(
        track_name="Albert Park Circuit",
        race_laps=58,
        base_lap_time=80.0,
        track_temp=25.0,
        track_abrasiveness=1.0,
        pit_loss_time=22.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=2
    ),
    
    "Japan": RaceConfig(
        track_name="Suzuka International Racing Course",
        race_laps=53,
        base_lap_time=91.0,
        track_temp=22.0,
        track_abrasiveness=1.1,
        pit_loss_time=21.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=2
    ),
    
    "China": RaceConfig(
        track_name="Shanghai International Circuit",
        race_laps=56,
        base_lap_time=94.0,
        track_temp=20.0,
        track_abrasiveness=1.0,
        pit_loss_time=22.0,
        overtaking_difficulty="EASY",
        drs_zones=2
    ),
    
    "Miami": RaceConfig(
        track_name="Miami International Autodrome",
        race_laps=57,
        base_lap_time=90.0,
        track_temp=30.0,
        track_abrasiveness=1.3,
        pit_loss_time=23.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=3
    ),
    
    "Imola": RaceConfig(
        track_name="Autodromo Enzo e Dino Ferrari",
        race_laps=63,
        base_lap_time=77.0,
        track_temp=24.0,
        track_abrasiveness=0.9,
        pit_loss_time=21.0,
        overtaking_difficulty="HARD",
        drs_zones=2
    ),
    
    "Monaco": RaceConfig(
        track_name="Circuit de Monaco",
        race_laps=78,
        base_lap_time=72.0,
        track_temp=22.0,
        track_abrasiveness=0.8,
        pit_loss_time=25.0,
        overtaking_difficulty="HARD",
        drs_zones=1
    ),
    
    "Canada": RaceConfig(
        track_name="Circuit Gilles Villeneuve",
        race_laps=70,
        base_lap_time=73.0,
        track_temp=20.0,
        track_abrasiveness=0.9,
        pit_loss_time=21.0,
        overtaking_difficulty="EASY",
        drs_zones=2
    ),
    
    "Spain": RaceConfig(
        track_name="Circuit de Barcelona-Catalunya",
        race_laps=66,
        base_lap_time=78.0,
        track_temp=28.0,
        track_abrasiveness=1.2,
        pit_loss_time=21.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=2
    ),
    
    "Austria": RaceConfig(
        track_name="Red Bull Ring",
        race_laps=71,
        base_lap_time=65.0,
        track_temp=24.0,
        track_abrasiveness=1.0,
        pit_loss_time=20.0,
        overtaking_difficulty="EASY",
        drs_zones=3
    ),
    
    "Great Britain": RaceConfig(
        track_name="Silverstone Circuit",
        race_laps=52,
        base_lap_time=87.0,
        track_temp=20.0,
        track_abrasiveness=1.1,
        pit_loss_time=21.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=2
    ),
    
    "Hungary": RaceConfig(
        track_name="Hungaroring",
        race_laps=70,
        base_lap_time=77.0,
        track_temp=32.0,
        track_abrasiveness=1.0,
        pit_loss_time=22.0,
        overtaking_difficulty="HARD",
        drs_zones=2
    ),
    
    "Belgium": RaceConfig(
        track_name="Circuit de Spa-Francorchamps",
        race_laps=44,
        base_lap_time=105.0,
        track_temp=18.0,
        track_abrasiveness=0.9,
        pit_loss_time=20.0,
        overtaking_difficulty="EASY",
        drs_zones=2
    ),
    
    "Netherlands": RaceConfig(
        track_name="Circuit Zandvoort",
        race_laps=72,
        base_lap_time=71.0,
        track_temp=20.0,
        track_abrasiveness=1.0,
        pit_loss_time=21.0,
        overtaking_difficulty="HARD",
        drs_zones=2
    ),
    
    "Italy": RaceConfig(
        track_name="Autodromo Nazionale di Monza",
        race_laps=53,
        base_lap_time=81.0,
        track_temp=28.0,
        track_abrasiveness=0.7,
        pit_loss_time=20.0,
        overtaking_difficulty="EASY",
        drs_zones=2
    ),
    
    "Azerbaijan": RaceConfig(
        track_name="Baku City Circuit",
        race_laps=51,
        base_lap_time=103.0,
        track_temp=30.0,
        track_abrasiveness=0.8,
        pit_loss_time=23.0,
        overtaking_difficulty="EASY",
        drs_zones=2
    ),
    
    "Singapore": RaceConfig(
        track_name="Marina Bay Street Circuit",
        race_laps=62,
        base_lap_time=100.0,
        track_temp=30.0,
        track_abrasiveness=1.3,
        pit_loss_time=24.0,
        overtaking_difficulty="HARD",
        drs_zones=3
    ),
    
    "United States": RaceConfig(
        track_name="Circuit of the Americas",
        race_laps=56,
        base_lap_time=96.0,
        track_temp=26.0,
        track_abrasiveness=1.1,
        pit_loss_time=22.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=2
    ),
    
    "Mexico": RaceConfig(
        track_name="Autodromo Hermanos Rodriguez",
        race_laps=71,
        base_lap_time=77.0,
        track_temp=24.0,
        track_abrasiveness=1.0,
        pit_loss_time=21.0,
        overtaking_difficulty="EASY",
        drs_zones=3
    ),
    
    "Brazil": RaceConfig(
        track_name="Autodromo Jose Carlos Pace (Interlagos)",
        race_laps=71,
        base_lap_time=70.0,
        track_temp=26.0,
        track_abrasiveness=1.0,
        pit_loss_time=20.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=2
    ),
    
    "Las Vegas": RaceConfig(
        track_name="Las Vegas Street Circuit",
        race_laps=50,
        base_lap_time=96.0,
        track_temp=15.0,
        track_abrasiveness=0.8,
        pit_loss_time=23.0,
        overtaking_difficulty="EASY",
        drs_zones=2
    ),
    
    "Qatar": RaceConfig(
        track_name="Lusail International Circuit",
        race_laps=57,
        base_lap_time=84.0,
        track_temp=28.0,
        track_abrasiveness=1.1,
        pit_loss_time=22.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=2
    ),
    
    "Abu Dhabi": RaceConfig(
        track_name="Yas Marina Circuit",
        race_laps=58,
        base_lap_time=86.0,
        track_temp=30.0,
        track_abrasiveness=1.0,
        pit_loss_time=22.0,
        overtaking_difficulty="MEDIUM",
        drs_zones=2
    ),
}


def get_track_config(track_name: str) -> RaceConfig:
    """
    Get configuration for a specific track.
    
    Args:
        track_name: Name of the track (e.g., "Monaco", "Spa", "Silverstone")
    
    Returns:
        RaceConfig for the specified track
    
    Raises:
        KeyError: If track not found
    """
    if track_name not in TRACK_DATABASE:
        available = ", ".join(TRACK_DATABASE.keys())
        raise KeyError(f"Track '{track_name}' not found. Available tracks: {available}")
    
    return TRACK_DATABASE[track_name]


def list_all_tracks() -> list:
    """Get list of all available track names."""
    return sorted(TRACK_DATABASE.keys())


def get_track_info(track_name: str) -> dict:
    """
    Get detailed information about a track.
    
    Args:
        track_name: Name of the track
    
    Returns:
        Dictionary with track characteristics
    """
    config = get_track_config(track_name)
    
    return {
        "name": config.track_name,
        "laps": config.race_laps,
        "lap_time": f"{config.base_lap_time:.1f}s",
        "temperature": f"{config.track_temp}°C",
        "tire_wear": _get_wear_description(config.track_abrasiveness),
        "overtaking": config.overtaking_difficulty,
        "drs_zones": config.drs_zones,
        "pit_loss": f"{config.pit_loss_time:.1f}s"
    }


def _get_wear_description(abrasiveness: float) -> str:
    """Convert abrasiveness value to description."""
    if abrasiveness < 0.8:
        return "Very Low"
    elif abrasiveness < 1.0:
        return "Low"
    elif abrasiveness < 1.1:
        return "Medium"
    elif abrasiveness < 1.2:
        return "High"
    else:
        return "Very High"


def print_track_database():
    """Print formatted list of all tracks."""
    print("\n" + "="*80)
    print("F1 TRACK DATABASE - 2024 CALENDAR")
    print("="*80)
    
    for i, track_name in enumerate(list_all_tracks(), 1):
        info = get_track_info(track_name)
        print(f"\n{i}. {track_name.upper()}")
        print(f"   Circuit: {info['name']}")
        print(f"   Laps: {info['laps']} | Lap Time: {info['lap_time']} | Temp: {info['temperature']}")
        print(f"   Tire Wear: {info['tire_wear']} | Overtaking: {info['overtaking']} | DRS: {info['drs_zones']} zones")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    # Demo: Print all tracks
    print_track_database()
    
    # Demo: Get specific track
    print("\n\nExample: Monaco Configuration")
    print("-" * 40)
    monaco = get_track_config("Monaco")
    print(f"Track: {monaco.track_name}")
    print(f"Laps: {monaco.race_laps}")
    print(f"Base Lap Time: {monaco.base_lap_time}s")
