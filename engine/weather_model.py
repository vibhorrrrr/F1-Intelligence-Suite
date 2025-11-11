"""
F1 Weather Impact Model

This module models weather effects on race strategy, including:
- Rain probability and intensity
- Track temperature changes
- Wet vs dry tire selection
- Lap time adjustments for weather conditions
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta


class WeatherCondition(Enum):
    """Weather condition types"""
    DRY = "DRY"
    DAMP = "DAMP"
    LIGHT_RAIN = "LIGHT_RAIN"
    HEAVY_RAIN = "HEAVY_RAIN"


class TrackCondition(Enum):
    """Track surface condition"""
    DRY = "DRY"
    DRYING = "DRYING"
    WET = "WET"
    SOAKED = "SOAKED"


@dataclass
class WeatherState:
    """Current weather state"""
    condition: WeatherCondition
    track_condition: TrackCondition
    track_temp: float  # Celsius
    air_temp: float  # Celsius
    humidity: float  # Percentage
    rain_intensity: float  # mm/hour
    wind_speed: float  # km/h


class WeatherModel:
    """
    Models weather impact on lap times and strategy decisions.
    
    Key considerations:
    - Rain can add 5-20 seconds per lap depending on intensity
    - Track drying creates strategic opportunities (crossover point)
    - Temperature affects tire performance
    - Weather changes force tire compound changes
    """
    
    # Lap time deltas for weather conditions (seconds)
    WEATHER_LAP_TIME_DELTA = {
        WeatherCondition.DRY: 0.0,
        WeatherCondition.DAMP: 2.0,
        WeatherCondition.LIGHT_RAIN: 8.0,
        WeatherCondition.HEAVY_RAIN: 15.0,
    }
    
    # Track drying rate (% per lap)
    TRACK_DRYING_RATE = 0.05  # 5% drier per lap without rain
    
    # Temperature effect on lap time (seconds per degree C from optimal)
    TEMP_EFFECT = 0.05
    OPTIMAL_TRACK_TEMP = 30.0
    
    def __init__(
        self,
        initial_weather: WeatherState,
        race_duration_minutes: int = 120
    ):
        """
        Initialize weather model.
        
        Args:
            initial_weather: Starting weather conditions
            race_duration_minutes: Expected race duration
        """
        self.current_weather = initial_weather
        self.race_duration = race_duration_minutes
        self.weather_history: List[WeatherState] = [initial_weather]
        
    def predict_weather_evolution(
        self,
        forecast_laps: int,
        rain_probability: float = 0.3
    ) -> List[WeatherState]:
        """
        Predict weather evolution over upcoming laps.
        
        Args:
            forecast_laps: Number of laps to forecast
            rain_probability: Probability of rain starting (0-1)
            
        Returns:
            List of predicted weather states
        """
        predictions = []
        current = self.current_weather
        
        for lap in range(forecast_laps):
            # Simulate weather changes
            if current.condition == WeatherCondition.DRY:
                # Check if rain starts
                if np.random.random() < rain_probability / forecast_laps:
                    new_condition = WeatherCondition.LIGHT_RAIN
                    rain_intensity = np.random.uniform(2.0, 8.0)
                else:
                    new_condition = WeatherCondition.DRY
                    rain_intensity = 0.0
            
            elif current.condition in [WeatherCondition.LIGHT_RAIN, WeatherCondition.HEAVY_RAIN]:
                # Rain can intensify, continue, or stop
                rand = np.random.random()
                if rand < 0.1:  # Rain stops
                    new_condition = WeatherCondition.DAMP
                    rain_intensity = 0.0
                elif rand < 0.8:  # Rain continues
                    new_condition = current.condition
                    rain_intensity = current.rain_intensity
                else:  # Rain intensifies
                    new_condition = WeatherCondition.HEAVY_RAIN
                    rain_intensity = min(20.0, current.rain_intensity * 1.5)
            
            else:  # DAMP
                # Track drying
                if np.random.random() < 0.7:
                    new_condition = WeatherCondition.DRY
                    rain_intensity = 0.0
                else:
                    new_condition = WeatherCondition.DAMP
                    rain_intensity = 0.0
            
            # Update track condition based on weather
            track_condition = self._determine_track_condition(
                new_condition,
                current.track_condition,
                rain_intensity
            )
            
            # Temperature changes
            track_temp = current.track_temp + np.random.uniform(-0.5, 0.5)
            air_temp = current.air_temp + np.random.uniform(-0.3, 0.3)
            
            new_weather = WeatherState(
                condition=new_condition,
                track_condition=track_condition,
                track_temp=track_temp,
                air_temp=air_temp,
                humidity=current.humidity,
                rain_intensity=rain_intensity,
                wind_speed=current.wind_speed
            )
            
            predictions.append(new_weather)
            current = new_weather
        
        return predictions
    
    def _determine_track_condition(
        self,
        weather: WeatherCondition,
        current_track: TrackCondition,
        rain_intensity: float
    ) -> TrackCondition:
        """Determine track condition based on weather."""
        if weather == WeatherCondition.HEAVY_RAIN:
            return TrackCondition.SOAKED
        elif weather == WeatherCondition.LIGHT_RAIN:
            return TrackCondition.WET
        elif weather == WeatherCondition.DAMP:
            return TrackCondition.DRYING
        else:  # DRY
            if current_track == TrackCondition.SOAKED:
                return TrackCondition.WET
            elif current_track == TrackCondition.WET:
                return TrackCondition.DRYING
            else:
                return TrackCondition.DRY
    
    def calculate_weather_lap_time_delta(
        self,
        weather: WeatherState,
        tire_type: str = "SLICK"  # SLICK, INTERMEDIATE, WET
    ) -> float:
        """
        Calculate lap time delta due to weather conditions.
        
        Args:
            weather: Current weather state
            tire_type: Type of tire being used
            
        Returns:
            Lap time delta in seconds (positive = slower)
        """
        base_delta = self.WEATHER_LAP_TIME_DELTA[weather.condition]
        
        # Temperature effect
        temp_delta = abs(weather.track_temp - self.OPTIMAL_TRACK_TEMP) * self.TEMP_EFFECT
        
        # Tire mismatch penalty
        tire_penalty = self._calculate_tire_mismatch_penalty(
            weather.condition,
            weather.track_condition,
            tire_type
        )
        
        total_delta = base_delta + temp_delta + tire_penalty
        
        return total_delta
    
    def _calculate_tire_mismatch_penalty(
        self,
        weather: WeatherCondition,
        track: TrackCondition,
        tire_type: str
    ) -> float:
        """
        Calculate penalty for using wrong tire type for conditions.
        
        Args:
            weather: Weather condition
            track: Track condition
            tire_type: Tire type being used
            
        Returns:
            Time penalty in seconds
        """
        # Optimal tire for conditions
        if track in [TrackCondition.SOAKED, TrackCondition.WET]:
            if weather == WeatherCondition.HEAVY_RAIN:
                optimal = "WET"
            else:
                optimal = "INTERMEDIATE"
        elif track == TrackCondition.DRYING:
            optimal = "INTERMEDIATE"
        else:
            optimal = "SLICK"
        
        # Penalty for mismatch
        if tire_type == optimal:
            return 0.0
        elif tire_type == "SLICK" and track != TrackCondition.DRY:
            # Slicks on wet track = very dangerous and slow
            return 20.0
        elif tire_type == "WET" and track == TrackCondition.DRY:
            # Wets on dry track = very slow
            return 10.0
        elif tire_type == "INTERMEDIATE":
            # Inters are versatile but not optimal
            return 2.0
        else:
            return 5.0
    
    def calculate_crossover_point(
        self,
        current_lap: int,
        weather_forecast: List[WeatherState]
    ) -> Optional[int]:
        """
        Calculate the crossover point where slicks become faster than inters.
        
        This is critical for strategy during drying conditions.
        
        Args:
            current_lap: Current race lap
            weather_forecast: Predicted weather evolution
            
        Returns:
            Lap number where crossover occurs, or None if no crossover
        """
        for i, weather in enumerate(weather_forecast):
            # Crossover when track is drying and rain has stopped
            if (weather.condition == WeatherCondition.DRY and
                weather.track_condition in [TrackCondition.DRYING, TrackCondition.DRY]):
                
                # Calculate lap times with both tire types
                slick_time = self.calculate_weather_lap_time_delta(weather, "SLICK")
                inter_time = self.calculate_weather_lap_time_delta(weather, "INTERMEDIATE")
                
                if slick_time < inter_time:
                    return current_lap + i
        
        return None
    
    def rain_probability_analysis(
        self,
        current_lap: int,
        remaining_laps: int,
        base_rain_probability: float = 0.3
    ) -> Dict[str, float]:
        """
        Analyze rain probability and strategic implications.
        
        Args:
            current_lap: Current race lap
            remaining_laps: Laps remaining
            base_rain_probability: Base probability of rain
            
        Returns:
            Dictionary with rain probability analysis
        """
        # Run multiple weather simulations
        num_simulations = 100
        rain_occurs_count = 0
        rain_lap_distribution = []
        
        for _ in range(num_simulations):
            forecast = self.predict_weather_evolution(
                remaining_laps,
                base_rain_probability
            )
            
            # Check if rain occurs
            rain_laps = [i for i, w in enumerate(forecast) 
                        if w.condition in [WeatherCondition.LIGHT_RAIN, WeatherCondition.HEAVY_RAIN]]
            
            if rain_laps:
                rain_occurs_count += 1
                rain_lap_distribution.append(current_lap + rain_laps[0])
        
        rain_probability = rain_occurs_count / num_simulations
        
        result = {
            'rain_probability': rain_probability,
            'expected_rain_lap': np.mean(rain_lap_distribution) if rain_lap_distribution else None,
            'rain_lap_std': np.std(rain_lap_distribution) if rain_lap_distribution else None,
            'strategic_recommendation': self._rain_strategy_recommendation(rain_probability)
        }
        
        return result
    
    def _rain_strategy_recommendation(self, rain_probability: float) -> str:
        """Generate strategy recommendation based on rain probability."""
        if rain_probability < 0.2:
            return "Low rain risk - proceed with dry strategy"
        elif rain_probability < 0.5:
            return "Moderate rain risk - consider flexible strategy, keep intermediates ready"
        elif rain_probability < 0.8:
            return "High rain risk - prepare for wet conditions, consider early pit stop"
        else:
            return "Rain imminent - switch to wet tires immediately"


class SafetyCarModel:
    """
    Models safety car probability and impact on strategy.
    
    Safety cars can neutralize gaps and create strategic opportunities.
    """
    
    # Base safety car probability per lap
    BASE_SC_PROBABILITY = 0.015  # ~1.5% per lap
    
    def __init__(self, race_laps: int):
        """
        Initialize safety car model.
        
        Args:
            race_laps: Total race laps
        """
        self.race_laps = race_laps
    
    def calculate_sc_probability(
        self,
        current_lap: int,
        weather: WeatherCondition,
        track_difficulty: float = 1.0
    ) -> float:
        """
        Calculate safety car probability for current conditions.
        
        Args:
            current_lap: Current race lap
            weather: Current weather condition
            track_difficulty: Track difficulty factor (1.0 = average)
            
        Returns:
            Probability of safety car this lap
        """
        base_prob = self.BASE_SC_PROBABILITY * track_difficulty
        
        # Weather increases SC probability
        weather_multiplier = {
            WeatherCondition.DRY: 1.0,
            WeatherCondition.DAMP: 1.5,
            WeatherCondition.LIGHT_RAIN: 2.5,
            WeatherCondition.HEAVY_RAIN: 4.0,
        }
        
        # First lap and restarts have higher SC probability
        if current_lap == 1:
            lap_multiplier = 3.0
        elif current_lap < 5:
            lap_multiplier = 1.5
        else:
            lap_multiplier = 1.0
        
        total_prob = base_prob * weather_multiplier[weather] * lap_multiplier
        
        return min(total_prob, 0.15)  # Cap at 15%
    
    def sc_strategy_impact(
        self,
        current_lap: int,
        last_pit_lap: int,
        gap_to_leader: float
    ) -> Dict[str, any]:
        """
        Analyze strategic impact of a safety car.
        
        Args:
            current_lap: Current race lap
            last_pit_lap: Lap of last pit stop
            gap_to_leader: Gap to race leader in seconds
            
        Returns:
            Dictionary with SC impact analysis
        """
        laps_since_pit = current_lap - last_pit_lap
        
        # SC neutralizes gaps
        gap_neutralization = min(gap_to_leader, gap_to_leader * 0.8)
        
        # Opportunity for "free" pit stop
        pit_opportunity = laps_since_pit > 10  # Worth pitting if >10 laps on tires
        
        return {
            'gap_neutralized': gap_neutralization,
            'pit_opportunity': pit_opportunity,
            'laps_since_pit': laps_since_pit,
            'recommendation': 'PIT NOW' if pit_opportunity else 'STAY OUT'
        }


if __name__ == "__main__":
    # Example usage
    print("=== F1 Weather Model Demo ===\n")
    
    # Initialize with dry conditions
    initial_weather = WeatherState(
        condition=WeatherCondition.DRY,
        track_condition=TrackCondition.DRY,
        track_temp=32.0,
        air_temp=25.0,
        humidity=60.0,
        rain_intensity=0.0,
        wind_speed=15.0
    )
    
    weather_model = WeatherModel(initial_weather)
    
    # Predict weather evolution
    print("=== Weather Forecast (Next 20 Laps) ===")
    forecast = weather_model.predict_weather_evolution(20, rain_probability=0.4)
    
    for i, weather in enumerate(forecast[::5], 1):  # Show every 5th lap
        print(f"Lap +{i*5}: {weather.condition.value}, "
              f"Track: {weather.track_condition.value}, "
              f"Temp: {weather.track_temp:.1f}°C")
    
    # Rain probability analysis
    print("\n=== Rain Probability Analysis ===")
    rain_analysis = weather_model.rain_probability_analysis(
        current_lap=20,
        remaining_laps=37,
        base_rain_probability=0.35
    )
    
    print(f"Rain probability: {rain_analysis['rain_probability']:.1%}")
    if rain_analysis['expected_rain_lap']:
        print(f"Expected rain lap: {rain_analysis['expected_rain_lap']:.0f}")
    print(f"Strategy: {rain_analysis['strategic_recommendation']}")
    
    # Crossover point calculation
    print("\n=== Crossover Point Analysis ===")
    crossover = weather_model.calculate_crossover_point(25, forecast)
    if crossover:
        print(f"Slicks faster than inters from lap: {crossover}")
    else:
        print("No crossover point detected - stay on current tires")
    
    # Safety car model
    print("\n=== Safety Car Probability ===")
    sc_model = SafetyCarModel(race_laps=57)
    
    for lap, condition in [(1, WeatherCondition.DRY), 
                           (20, WeatherCondition.DRY),
                           (20, WeatherCondition.LIGHT_RAIN)]:
        prob = sc_model.calculate_sc_probability(lap, condition)
        print(f"Lap {lap}, {condition.value}: {prob:.1%} SC probability")
