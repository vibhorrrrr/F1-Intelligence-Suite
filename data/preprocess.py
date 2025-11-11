"""
F1 Data Preprocessing Pipeline

This module provides data cleaning, transformation, and feature engineering
for F1 race data to prepare it for analysis and modeling.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import timedelta


class F1DataPreprocessor:
    """
    Preprocesses F1 race data for analysis and modeling.
    
    Handles:
    - Data cleaning and validation
    - Feature engineering
    - Outlier detection
    - Data normalization
    """
    
    def __init__(self):
        """Initialize preprocessor."""
        self.compound_encoding = {
            'SOFT': 0,
            'MEDIUM': 1,
            'HARD': 2,
            'INTERMEDIATE': 3,
            'WET': 4
        }
    
    def clean_lap_data(
        self,
        lap_data: pd.DataFrame,
        remove_outliers: bool = True
    ) -> pd.DataFrame:
        """
        Clean and validate lap data.
        
        Args:
            lap_data: Raw lap data DataFrame
            remove_outliers: Whether to remove outlier lap times
            
        Returns:
            Cleaned DataFrame
        """
        if lap_data.empty:
            return lap_data
        
        df = lap_data.copy()
        
        # Remove invalid lap times (NaN, negative, or unrealistic)
        df = df[df['lap_time'].notna()]
        df = df[df['lap_time'] > 0]
        df = df[df['lap_time'] < 300]  # No lap should be > 5 minutes
        
        # Remove outliers using IQR method
        if remove_outliers:
            Q1 = df['lap_time'].quantile(0.25)
            Q3 = df['lap_time'].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            df = df[(df['lap_time'] >= lower_bound) & (df['lap_time'] <= upper_bound)]
        
        # Sort by lap number
        df = df.sort_values(['driver', 'lap_number']).reset_index(drop=True)
        
        return df
    
    def engineer_features(
        self,
        lap_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Engineer features for modeling.
        
        Args:
            lap_data: Cleaned lap data
            
        Returns:
            DataFrame with additional features
        """
        if lap_data.empty:
            return lap_data
        
        df = lap_data.copy()
        
        # Encode tire compound
        df['compound_encoded'] = df['compound'].map(self.compound_encoding)
        
        # Calculate tire degradation proxy
        df['tire_deg_proxy'] = df.groupby(['driver', 'stint'])['tire_life'].transform(
            lambda x: (x - x.min()) / (x.max() - x.min() + 1)
        )
        
        # Calculate lap time delta from personal best
        df['delta_to_best'] = df.groupby('driver')['lap_time'].transform(
            lambda x: x - x.min()
        )
        
        # Rolling average lap time (3-lap window)
        df['lap_time_rolling_avg'] = df.groupby('driver')['lap_time'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        
        # Lap time trend (improving or degrading)
        df['lap_time_trend'] = df.groupby('driver')['lap_time'].transform(
            lambda x: x.diff()
        )
        
        # Fuel load proxy (decreases linearly with laps)
        max_lap = df['lap_number'].max()
        df['fuel_load_proxy'] = 110.0 * (1 - df['lap_number'] / max_lap)
        
        # Stint progress (0 to 1)
        df['stint_progress'] = df.groupby(['driver', 'stint'])['tire_life'].transform(
            lambda x: x / x.max()
        )
        
        # Is this a pit lap? (next stint is different)
        df['is_pit_lap'] = df.groupby('driver')['stint'].transform(
            lambda x: x.diff().shift(-1).fillna(0) != 0
        ).astype(int)
        
        return df
    
    def calculate_pace_metrics(
        self,
        lap_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate pace metrics for each driver.
        
        Args:
            lap_data: Lap data with features
            
        Returns:
            DataFrame with pace metrics per driver
        """
        if lap_data.empty:
            return pd.DataFrame()
        
        pace_metrics = lap_data.groupby('driver').agg({
            'lap_time': ['mean', 'std', 'min', 'max'],
            'lap_number': 'count',
            'compound': lambda x: x.mode()[0] if len(x) > 0 else None,
        }).reset_index()
        
        pace_metrics.columns = [
            'driver', 'avg_lap_time', 'lap_time_std',
            'best_lap_time', 'worst_lap_time', 'total_laps', 'most_used_compound'
        ]
        
        # Calculate consistency score (lower std = more consistent)
        pace_metrics['consistency_score'] = 1 / (1 + pace_metrics['lap_time_std'])
        
        # Calculate pace relative to fastest driver
        fastest_avg = pace_metrics['avg_lap_time'].min()
        pace_metrics['pace_delta_to_fastest'] = pace_metrics['avg_lap_time'] - fastest_avg
        
        return pace_metrics
    
    def extract_stint_data(
        self,
        lap_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Extract stint-level data from lap data.
        
        Args:
            lap_data: Lap data
            
        Returns:
            DataFrame with stint information
        """
        if lap_data.empty:
            return pd.DataFrame()
        
        stint_data = lap_data.groupby(['driver', 'stint']).agg({
            'lap_number': ['min', 'max', 'count'],
            'compound': 'first',
            'lap_time': ['mean', 'min', 'max'],
            'tire_life': 'max',
        }).reset_index()
        
        stint_data.columns = [
            'driver', 'stint', 'start_lap', 'end_lap', 'stint_length',
            'compound', 'avg_lap_time', 'best_lap_time', 'worst_lap_time',
            'max_tire_life'
        ]
        
        # Calculate stint degradation
        stint_data['stint_degradation'] = (
            stint_data['worst_lap_time'] - stint_data['best_lap_time']
        )
        
        return stint_data
    
    def identify_pit_windows(
        self,
        lap_data: pd.DataFrame,
        compound: str = 'MEDIUM'
    ) -> Tuple[int, int]:
        """
        Identify optimal pit window from historical data.
        
        Args:
            lap_data: Lap data
            compound: Tire compound to analyze
            
        Returns:
            Tuple of (earliest_optimal_lap, latest_optimal_lap)
        """
        if lap_data.empty:
            return (15, 30)
        
        # Filter for specific compound
        compound_data = lap_data[lap_data['compound'] == compound].copy()
        
        if compound_data.empty:
            return (15, 30)
        
        # Find when lap times start degrading significantly
        avg_by_tire_life = compound_data.groupby('tire_life')['lap_time'].mean()
        
        if len(avg_by_tire_life) < 5:
            return (15, 30)
        
        # Find inflection point (where degradation accelerates)
        degradation_rate = avg_by_tire_life.diff()
        
        # Optimal window: before degradation accelerates
        threshold = degradation_rate.mean() + degradation_rate.std()
        
        critical_laps = degradation_rate[degradation_rate > threshold].index.tolist()
        
        if critical_laps:
            earliest = max(10, int(critical_laps[0] * 0.7))
            latest = int(critical_laps[0])
        else:
            earliest = 15
            latest = 30
        
        return (earliest, latest)
    
    def normalize_data(
        self,
        df: pd.DataFrame,
        columns: List[str]
    ) -> pd.DataFrame:
        """
        Normalize specified columns to 0-1 range.
        
        Args:
            df: DataFrame to normalize
            columns: List of column names to normalize
            
        Returns:
            DataFrame with normalized columns
        """
        result = df.copy()
        
        for col in columns:
            if col in result.columns:
                min_val = result[col].min()
                max_val = result[col].max()
                
                if max_val > min_val:
                    result[f'{col}_normalized'] = (result[col] - min_val) / (max_val - min_val)
                else:
                    result[f'{col}_normalized'] = 0.0
        
        return result
    
    def create_training_dataset(
        self,
        lap_data: pd.DataFrame,
        target_column: str = 'lap_time'
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create training dataset for machine learning models.
        
        Args:
            lap_data: Preprocessed lap data
            target_column: Target variable column name
            
        Returns:
            Tuple of (features DataFrame, target Series)
        """
        if lap_data.empty:
            return pd.DataFrame(), pd.Series()
        
        # Engineer features first
        df = self.engineer_features(lap_data)
        
        # Select feature columns
        feature_columns = [
            'lap_number',
            'compound_encoded',
            'tire_life',
            'tire_deg_proxy',
            'fuel_load_proxy',
            'stint_progress',
        ]
        
        # Filter to available columns
        available_features = [col for col in feature_columns if col in df.columns]
        
        X = df[available_features].copy()
        y = df[target_column].copy()
        
        # Remove rows with NaN
        valid_indices = X.notna().all(axis=1) & y.notna()
        X = X[valid_indices]
        y = y[valid_indices]
        
        return X, y


class DataValidator:
    """
    Validates F1 data quality and consistency.
    """
    
    @staticmethod
    def validate_lap_data(lap_data: pd.DataFrame) -> Dict[str, any]:
        """
        Validate lap data quality.
        
        Args:
            lap_data: Lap data to validate
            
        Returns:
            Dictionary with validation results
        """
        if lap_data.empty:
            return {'valid': False, 'error': 'Empty dataset'}
        
        issues = []
        
        # Check for required columns
        required_columns = ['lap_number', 'driver', 'lap_time']
        missing_columns = [col for col in required_columns if col not in lap_data.columns]
        
        if missing_columns:
            issues.append(f"Missing columns: {missing_columns}")
        
        # Check for negative lap times
        if 'lap_time' in lap_data.columns:
            negative_times = (lap_data['lap_time'] < 0).sum()
            if negative_times > 0:
                issues.append(f"{negative_times} negative lap times found")
        
        # Check for unrealistic lap times
        if 'lap_time' in lap_data.columns:
            unrealistic = ((lap_data['lap_time'] < 60) | (lap_data['lap_time'] > 300)).sum()
            if unrealistic > 0:
                issues.append(f"{unrealistic} unrealistic lap times found")
        
        # Check for missing values
        missing_values = lap_data.isnull().sum().sum()
        if missing_values > 0:
            issues.append(f"{missing_values} missing values found")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_rows': len(lap_data),
            'total_columns': len(lap_data.columns)
        }


if __name__ == "__main__":
    # Example usage
    print("="*60)
    print("F1 DATA PREPROCESSING DEMO")
    print("="*60)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'lap_number': list(range(1, 31)) * 2,
        'driver': ['VER'] * 30 + ['HAM'] * 30,
        'team': ['Red Bull Racing'] * 30 + ['Mercedes'] * 30,
        'lap_time': np.random.normal(90, 2, 60) + np.linspace(0, 3, 60),
        'compound': ['MEDIUM'] * 20 + ['HARD'] * 10 + ['MEDIUM'] * 20 + ['HARD'] * 10,
        'tire_life': list(range(1, 21)) + list(range(1, 11)) + list(range(1, 21)) + list(range(1, 11)),
        'stint': [1] * 20 + [2] * 10 + [1] * 20 + [2] * 10,
    })
    
    # Initialize preprocessor
    preprocessor = F1DataPreprocessor()
    
    # Validate data
    print("\n=== Data Validation ===")
    validator = DataValidator()
    validation_result = validator.validate_lap_data(sample_data)
    print(f"Valid: {validation_result['valid']}")
    print(f"Total rows: {validation_result['total_rows']}")
    print(f"Issues: {validation_result['issues']}")
    
    # Clean data
    print("\n=== Data Cleaning ===")
    cleaned_data = preprocessor.clean_lap_data(sample_data)
    print(f"Original rows: {len(sample_data)}")
    print(f"Cleaned rows: {len(cleaned_data)}")
    
    # Engineer features
    print("\n=== Feature Engineering ===")
    featured_data = preprocessor.engineer_features(cleaned_data)
    print(f"Original features: {len(sample_data.columns)}")
    print(f"Engineered features: {len(featured_data.columns)}")
    print(f"New features: {[col for col in featured_data.columns if col not in sample_data.columns]}")
    
    # Calculate pace metrics
    print("\n=== Pace Metrics ===")
    pace_metrics = preprocessor.calculate_pace_metrics(featured_data)
    print(pace_metrics.to_string())
    
    # Extract stint data
    print("\n=== Stint Data ===")
    stint_data = preprocessor.extract_stint_data(featured_data)
    print(stint_data.to_string())
