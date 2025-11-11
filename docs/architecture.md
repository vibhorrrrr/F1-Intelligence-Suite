# F1 Strategy Suite - System Architecture

## Overview

The F1 Race Strategy Intelligence Suite is built on a modular, layered architecture that separates concerns and enables extensibility. This document describes the system design, component interactions, and key design decisions.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Plotly Dash Dashboard (dashboard_app.py)       │  │
│  │  - Real-time visualization                               │  │
│  │  - Interactive controls                                  │  │
│  │  - Strategy recommendations                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        Simulation Engine (sim_engine.py)                 │  │
│  │  - Race orchestration                                    │  │
│  │  - Strategy optimization                                 │  │
│  │  - Real-time recommendations                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────┴──────────────────────────────┐   │
│  │              Domain Models (engine/)                     │   │
│  │                                                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │Tire Model  │  │Pit Optimizer│  │Fuel Model  │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │Weather     │  │Opponent    │  │ERS Model   │        │   │
│  │  │Model       │  │Model       │  │            │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                         DATA LAYER                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Data Management (data/)                          │  │
│  │                                                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │  │
│  │  │Loaders     │  │Preprocessor│  │Validators  │        │  │
│  │  │(FastF1)    │  │            │  │            │        │  │
│  │  └────────────┘  └────────────┘  └────────────┘        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │      Live Telemetry (live/)                              │  │
│  │                                                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │  │
│  │  │OpenF1 API  │  │Stream      │  │Mock Data   │        │  │
│  │  │Client      │  │Monitor     │  │Generator   │        │  │
│  │  └────────────┘  └────────────┘  └────────────┘        │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Presentation Layer

#### Dashboard (ui/dashboard_app.py)
**Responsibility:** User interface and visualization

**Key Features:**
- Real-time data visualization using Plotly
- Interactive controls for strategy simulation
- Live position tracking
- Tire degradation curves
- Strategy recommendations

**Technology:**
- Plotly Dash framework
- Custom CSS for F1-inspired theme
- Callback-based interactivity

**Design Pattern:** MVC (Model-View-Controller)
- Model: Simulation engine
- View: Dash components
- Controller: Callbacks

---

### 2. Application Layer

#### Simulation Engine (engine/sim_engine.py)
**Responsibility:** Orchestrate race simulation and strategy optimization

**Core Functions:**
```python
def simulate_race(strategy, starting_position) -> SimulationResult
def optimize_strategy(max_stops, starting_position) -> List[SimulationResult]
def real_time_recommendation(current_state) -> Dict[str, any]
def compare_strategies(strategies) -> None
```

**Design Pattern:** Facade
- Provides simplified interface to complex subsystems
- Coordinates multiple domain models
- Handles cross-cutting concerns

---

### 3. Domain Models

#### Tire Model (engine/tire_model.py)
**Responsibility:** Model tire degradation and performance

**Key Classes:**
- `TireDegradationModel`: Physics-based degradation
- `MLTireDegradationModel`: Machine learning approach (future)

**Mathematical Model:**
```
degradation = 1 - exp(-rate × laps × factors)
lap_time = base_time + compound_delta + deg_effect + fuel_effect
```

**Design Pattern:** Strategy Pattern
- Different degradation algorithms (physics vs. ML)
- Swappable implementations

---

#### Pit Optimizer (engine/pit_optimizer.py)
**Responsibility:** Optimize pit stop timing and strategy

**Key Classes:**
- `PitStrategyOptimizer`: Main optimization engine
- `RaceStrategy`: Strategy representation
- `PitStopEvent`: Individual pit stop

**Algorithms:**
1. **Deterministic Optimization:**
   - Enumerate strategy combinations
   - Simulate each strategy
   - Rank by total race time

2. **Monte Carlo Simulation:**
   - Add randomness (pit stop variance, safety cars)
   - Run 1,000+ iterations
   - Statistical analysis (mean, std dev, percentiles)

**Design Pattern:** Builder Pattern
- Construct complex strategies incrementally
- Validate constraints (2+ compounds, fuel, etc.)

---

#### Fuel Model (engine/fuel_model.py)
**Responsibility:** Model fuel consumption and weight effects

**Key Features:**
- Fuel consumption by mode (PUSH, NORMAL, SAVING)
- Weight effect on lap time (0.03s/kg)
- Fuel-saving benefit calculation
- ERS deployment optimization

**Design Pattern:** Value Object
- Immutable fuel state
- Pure functions for calculations

---

#### Weather Model (engine/weather_model.py)
**Responsibility:** Model weather impact and forecasting

**Key Features:**
- Weather evolution prediction
- Rain probability analysis
- Crossover point calculation (slicks vs. inters)
- Safety car probability

**Design Pattern:** State Pattern
- Weather conditions as states
- Transitions between states
- State-specific behavior

---

#### Opponent Model (engine/opponent_model.py)
**Responsibility:** Model opponent behavior and competitive dynamics

**Key Features:**
- Pace prediction
- Overtaking probability
- Undercut threat assessment
- Battle simulation

**Design Pattern:** Entity Pattern
- Drivers as entities with attributes
- Behavior based on entity state

---

### 4. Data Layer

#### Data Loaders (data/loaders.py)
**Responsibility:** Load historical F1 data

**Data Sources:**
- FastF1 API (official timing data)
- Track information database
- Historical race results

**Design Pattern:** Repository Pattern
- Abstract data access
- Consistent interface regardless of source

---

#### Preprocessor (data/preprocess.py)
**Responsibility:** Clean and transform data

**Pipeline:**
1. Data validation
2. Outlier removal
3. Feature engineering
4. Normalization
5. Training dataset creation

**Design Pattern:** Pipeline Pattern
- Sequential transformations
- Composable operations

---

#### Live Telemetry (live/openf1_stream.py)
**Responsibility:** Stream real-time race data

**Components:**
- `OpenF1Client`: API client
- `LiveStrategyMonitor`: Real-time monitoring
- `MockLiveDataGenerator`: Testing/demo

**Design Pattern:** Observer Pattern
- Subscribe to data updates
- Callback-based notifications

---

## Design Principles

### 1. Separation of Concerns
Each module has a single, well-defined responsibility:
- **Engine**: Business logic and simulation
- **Data**: Data access and transformation
- **UI**: Presentation and user interaction
- **Live**: Real-time data streaming

### 2. Dependency Injection
Components receive dependencies through constructors:
```python
def __init__(self, tire_model: TireDegradationModel, ...):
    self.tire_model = tire_model
```

**Benefits:**
- Testability (mock dependencies)
- Flexibility (swap implementations)
- Clear dependencies

### 3. Type Safety
Full type hints throughout codebase:
```python
def predict_lap_time(
    self,
    compound: TireCompound,
    lap_number: int,
    fuel_load: float = 100.0
) -> float:
```

**Benefits:**
- IDE autocomplete
- Static type checking (mypy)
- Self-documenting code

### 4. Immutability
Use dataclasses and immutable objects where possible:
```python
@dataclass(frozen=True)
class PitStopEvent:
    lap: int
    in_compound: TireCompound
    out_compound: TireCompound
```

**Benefits:**
- Thread safety
- Predictable behavior
- Easier reasoning

### 5. Composition Over Inheritance
Favor composition:
```python
class F1SimulationEngine:
    def __init__(self, config: RaceConfig):
        self.tire_model = TireDegradationModel(...)
        self.pit_optimizer = PitStrategyOptimizer(...)
        self.fuel_model = FuelModel(...)
```

**Benefits:**
- Flexibility
- Avoid deep inheritance hierarchies
- Easier testing

---

## Data Flow

### Race Simulation Flow

```
1. User initiates simulation
   ↓
2. SimulationEngine receives strategy
   ↓
3. For each lap:
   ├─→ TireModel calculates degradation
   ├─→ FuelModel calculates weight effect
   ├─→ WeatherModel applies conditions
   └─→ OpponentModel calculates traffic
   ↓
4. Aggregate lap times
   ↓
5. Return SimulationResult
```

### Real-Time Update Flow

```
1. OpenF1Client polls API (every 2s)
   ↓
2. LiveStrategyMonitor receives update
   ↓
3. Update callback triggered
   ↓
4. Dashboard processes update
   ↓
5. SimulationEngine generates recommendation
   ↓
6. Dashboard re-renders
```

---

## Performance Considerations

### 1. Vectorization
Use NumPy for batch calculations:
```python
# Instead of loop
degradation = [calc_deg(lap) for lap in range(40)]

# Use vectorization
laps = np.arange(40)
degradation = 1 - np.exp(-rate * laps)
```

### 2. Caching
Cache expensive calculations:
```python
@lru_cache(maxsize=128)
def calculate_degradation(compound, lap, fuel):
    # Expensive calculation
    return result
```

### 3. Lazy Evaluation
Compute only when needed:
```python
# Don't precompute all strategies
# Generate on demand during optimization
```

### 4. Profiling
Regular performance profiling:
```bash
python -m cProfile -o profile.stats sim_engine.py
python -m pstats profile.stats
```

---

## Testing Strategy

### Unit Tests
Test individual components in isolation:
```python
def test_tire_degradation():
    model = TireDegradationModel(...)
    deg = model.calculate_degradation(TireCompound.SOFT, 10)
    assert 0 <= deg <= 1
```

### Integration Tests
Test component interactions:
```python
def test_simulation_engine():
    engine = F1SimulationEngine(config)
    result = engine.simulate_race(strategy, position=10)
    assert result.total_race_time > 0
```

### Validation Tests
Compare against real data:
```python
def test_bahrain_2024_validation():
    # Load real race data
    real_data = load_bahrain_2024()
    
    # Simulate
    simulated = engine.simulate_race(...)
    
    # Compare
    assert abs(simulated.time - real_data.time) < tolerance
```

---

## Extensibility

### Adding New Models

1. **Create model class:**
```python
class NewModel:
    def __init__(self, params):
        self.params = params
    
    def calculate(self, inputs):
        # Implementation
        return result
```

2. **Integrate with engine:**
```python
class F1SimulationEngine:
    def __init__(self, config):
        # ...
        self.new_model = NewModel(config.new_params)
```

3. **Update simulation loop:**
```python
def simulate_race(self, strategy):
    # ...
    new_effect = self.new_model.calculate(...)
    lap_time += new_effect
```

### Adding New Data Sources

1. **Implement loader:**
```python
class NewDataLoader:
    def load_data(self, params):
        # Fetch from new source
        return data
```

2. **Standardize format:**
```python
def transform_to_standard(raw_data):
    # Convert to common format
    return standardized_data
```

---

## Security Considerations

### API Keys
- Store in environment variables
- Never commit to version control
- Use `.env` files (gitignored)

### Input Validation
- Validate all user inputs
- Sanitize data from external APIs
- Handle edge cases gracefully

### Error Handling
- Try-except blocks for external calls
- Graceful degradation
- Informative error messages

---

## Deployment

### Local Development
```bash
python ui/dashboard_app.py
```

### Production Deployment
Options:
1. **Heroku**: Simple deployment
2. **AWS EC2**: Full control
3. **Docker**: Containerized deployment
4. **Streamlit Cloud**: For Streamlit version

### Environment Variables
```bash
OPENF1_API_KEY=your_key
CACHE_DIR=/path/to/cache
DEBUG=False
```

---

## Future Architecture Improvements

### 1. Microservices
Split into separate services:
- Simulation service
- Data service
- API gateway
- Dashboard frontend

### 2. Message Queue
Add async processing:
- RabbitMQ or Redis
- Background simulation jobs
- Real-time event streaming

### 3. Database
Add persistent storage:
- PostgreSQL for structured data
- Redis for caching
- TimescaleDB for time-series

### 4. API Layer
RESTful API:
```
POST /api/simulate
GET /api/strategies
GET /api/live/positions
```

---

## Conclusion

This architecture provides:
- ✅ **Modularity**: Easy to understand and modify
- ✅ **Testability**: Components can be tested in isolation
- ✅ **Extensibility**: New features can be added easily
- ✅ **Performance**: Optimized for speed and efficiency
- ✅ **Maintainability**: Clean code with clear responsibilities
