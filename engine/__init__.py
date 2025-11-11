"""
F1 Strategy Suite - Engine Package

Core simulation modules for F1 race strategy analysis.
"""

from engine.tire_model import TireCompound, TireDegradationModel
from engine.pit_optimizer import PitStrategyOptimizer, RaceStrategy, PitStopEvent
from engine.fuel_model import FuelModel, ERSModel
from engine.weather_model import WeatherModel, WeatherState, WeatherCondition
from engine.opponent_model import OpponentPaceModel, Driver, OpponentState
from engine.sim_engine import F1SimulationEngine, RaceConfig

__all__ = [
    'TireCompound',
    'TireDegradationModel',
    'PitStrategyOptimizer',
    'RaceStrategy',
    'PitStopEvent',
    'FuelModel',
    'ERSModel',
    'WeatherModel',
    'WeatherState',
    'WeatherCondition',
    'OpponentPaceModel',
    'Driver',
    'OpponentState',
    'F1SimulationEngine',
    'RaceConfig',
]
