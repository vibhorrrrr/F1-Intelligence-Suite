"""
F1 Strategy Suite - Modern Landing Page
Inspired by professional SaaS design patterns
With interactive expandable cards and glow effects
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

# Initialize app with Bootstrap theme
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.CYBORG], 
    suppress_callback_exceptions=True,
    requests_pathname_prefix='/'
)
server = app.server  # Expose the server for WSGI
app.title = "F1 Strategy Intelligence Suite"

# Color scheme
COLORS = {
    'primary': '#00D9FF',      # Cyan accent
    'secondary': '#10B981',    # Green
    'background': '#0A0E27',   # Deep navy
    'surface': '#1A1F3A',      # Lighter navy
    'card': '#252B48',         # Card background
    'text': '#E5E7EB',         # Light gray
    'text_secondary': '#9CA3AF', # Medium gray
    'border': '#374151',       # Border gray
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Orange
    'danger': '#EF4444',       # Red
}

# Custom CSS with glow effects
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .feature-card {
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: pointer;
                position: relative;
            }
            
            .feature-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 20px 60px rgba(0, 217, 255, 0.4), 
                            0 0 40px rgba(0, 217, 255, 0.3),
                            inset 0 0 20px rgba(0, 217, 255, 0.1);
                border-color: #00D9FF !important;
            }
            
            .feature-card:hover::before {
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #00D9FF, #10B981, #8B5CF6, #00D9FF);
                border-radius: 14px;
                z-index: -1;
                filter: blur(10px);
                opacity: 0.7;
                animation: glow-rotate 3s linear infinite;
            }
            
            @keyframes glow-rotate {
                0% { filter: blur(10px) hue-rotate(0deg); }
                100% { filter: blur(10px) hue-rotate(360deg); }
            }
            
            .card-expanded {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) !important;
                width: 90%;
                max-width: 800px;
                max-height: 85vh;
                overflow-y: auto;
                z-index: 1000;
                box-shadow: 0 25px 100px rgba(0, 0, 0, 0.8);
            }
            
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.85);
                z-index: 999;
                backdrop-filter: blur(5px);
            }
            
            .close-btn {
                position: absolute;
                top: 20px;
                right: 20px;
                background: transparent;
                border: 2px solid #00D9FF;
                color: #00D9FF;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                font-size: 24px;
                cursor: pointer;
                transition: all 0.3s;
                z-index: 10;
            }
            
            .close-btn:hover {
                background: #00D9FF;
                color: #000;
                transform: rotate(90deg);
            }
            
            /* Custom scrollbar for modal */
            .card-expanded::-webkit-scrollbar {
                width: 8px;
            }
            
            .card-expanded::-webkit-scrollbar-track {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
            }
            
            .card-expanded::-webkit-scrollbar-thumb {
                background: #00D9FF;
                border-radius: 4px;
            }
            
            .card-expanded::-webkit-scrollbar-thumb:hover {
                background: #10B981;
            }
            
            /* Bullet point styling */
            .bullet-point::before {
                content: '▸';
                color: #00D9FF;
                font-weight: bold;
                display: inline-block;
                width: 1em;
                margin-left: -1em;
            }
            
            /* F1-themed wave animations - SVG waves */
            .racing-waves {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                z-index: 0;
                pointer-events: none;
            }
            
            .wave {
                position: absolute;
                width: 200%;
                height: 100%;
                left: 0;
            }
            
            .wave1 {
                background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320' preserveAspectRatio='none'%3E%3Cpath d='M0,160 Q360,64 720,160 T1440,160 L1440,320 L0,320 Z' fill='rgba(0,217,255,0.15)'/%3E%3C/svg%3E");
                background-size: 100% 400px;
                background-repeat: repeat-x;
                animation: wave-animation 20s linear infinite;
                top: 0;
                height: 400px;
                opacity: 1;
            }
            
            .wave2 {
                background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320' preserveAspectRatio='none'%3E%3Cpath d='M0,192 Q360,96 720,192 T1440,192 L1440,320 L0,320 Z' fill='rgba(16,185,129,0.12)'/%3E%3C/svg%3E");
                background-size: 100% 400px;
                background-repeat: repeat-x;
                animation: wave-animation 25s linear infinite reverse;
                top: 25%;
                height: 400px;
                opacity: 1;
            }
            
            .wave3 {
                background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320' preserveAspectRatio='none'%3E%3Cpath d='M0,128 Q360,224 720,128 T1440,128 L1440,320 L0,320 Z' fill='rgba(139,92,246,0.1)'/%3E%3C/svg%3E");
                background-size: 100% 400px;
                background-repeat: repeat-x;
                animation: wave-animation 30s linear infinite;
                top: 50%;
                height: 400px;
                opacity: 1;
            }
            
            .wave4 {
                background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320' preserveAspectRatio='none'%3E%3Cpath d='M0,176 Q360,80 720,176 T1440,176 L1440,320 L0,320 Z' fill='rgba(0,217,255,0.08)'/%3E%3C/svg%3E");
                background-size: 100% 400px;
                background-repeat: repeat-x;
                animation: wave-animation 35s linear infinite reverse;
                bottom: 0;
                height: 400px;
                opacity: 1;
            }
            
            @keyframes wave-animation {
                0% { transform: translateX(0); }
                100% { transform: translateX(-50%); }
            }
            
            /* Speed lines animation */
            .speed-lines {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                z-index: 0;
                opacity: 0.15;
            }
            
            .speed-line {
                position: absolute;
                height: 2px;
                background: linear-gradient(90deg, transparent, #00D9FF, transparent);
                animation: speed-line-animation 3s linear infinite;
            }
            
            .speed-line:nth-child(1) { top: 20%; animation-delay: 0s; }
            .speed-line:nth-child(2) { top: 40%; animation-delay: 0.5s; }
            .speed-line:nth-child(3) { top: 60%; animation-delay: 1s; }
            .speed-line:nth-child(4) { top: 80%; animation-delay: 1.5s; }
            
            @keyframes speed-line-animation {
                0% { left: -100%; width: 0; }
                50% { width: 30%; }
                100% { left: 100%; width: 0; }
            }
            
            /* Contact link hover effects */
            a[href*="linkedin"]:hover,
            a[href*="mailto"]:hover {
                transform: translateY(-5px);
                border-color: #00D9FF !important;
                box-shadow: 0 10px 30px rgba(0, 217, 255, 0.3);
            }
            
            /* Dashboard button hover effects */
            a[href*="8050"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 217, 255, 0.4);
            }
            
            /* Top title bar */
            .top-title {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                background: rgba(10, 14, 39, 0.8);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(55, 65, 81, 0.3);
                z-index: 1000;
                padding: 15px 0;
                text-align: center;
            }
            
            /* macOS-style floating dock at bottom */
            .navbar {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(10, 14, 39, 0.4);
                backdrop-filter: blur(30px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 20px;
                z-index: 1000;
                padding: 10px 18px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                            0 0 0 1px rgba(255, 255, 255, 0.03) inset;
            }
            
            .nav-link {
                color: #E5E7EB;
                text-decoration: none;
                padding: 12px 20px;
                border-radius: 12px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                font-size: 14px;
                font-weight: 500;
                display: inline-flex;
                align-items: center;
                white-space: nowrap;
            }
            
            .nav-link:hover {
                background: rgba(0, 217, 255, 0.12);
                transform: translateY(-3px);
                color: #00D9FF;
            }
            
            .nav-link.active {
                background: rgba(0, 217, 255, 0.18);
                color: #00D9FF;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 217, 255, 0.25);
            }
            
            /* Smooth scrolling */
            html {
                scroll-behavior: smooth;
            }
            
            /* Section padding for navbar offset */
            section {
                scroll-margin-top: 80px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // Active section highlighting on scroll
            function updateActiveSection() {
                const sections = ['home', 'features', 'tech-stack', 'about'];
                const navLinks = ['nav-home', 'nav-features', 'nav-tech-stack', 'nav-about'];
                
                let currentSection = null;
                let minDistance = Infinity;
                
                // Find which section is closest to the top of viewport
                sections.forEach(function(sectionId) {
                    const section = document.getElementById(sectionId);
                    if (section) {
                        const rect = section.getBoundingClientRect();
                        const distance = Math.abs(rect.top - 100);
                        
                        // If section is in view and closer than previous
                        if (rect.top <= 200 && rect.bottom >= 0 && distance < minDistance) {
                            minDistance = distance;
                            currentSection = sectionId;
                        }
                    }
                });
                
                // Update active nav link - remove all active classes first
                navLinks.forEach(function(navId) {
                    const navLink = document.getElementById(navId);
                    if (navLink) {
                        navLink.classList.remove('active');
                    }
                });
                
                // Add active class only to current section
                if (currentSection) {
                    const activeNavLink = document.getElementById('nav-' + currentSection);
                    if (activeNavLink) {
                        activeNavLink.classList.add('active');
                    }
                }
            }
            
            // Run on scroll
            window.addEventListener('scroll', updateActiveSection);
            
            // Run on page load
            window.addEventListener('load', updateActiveSection);
            
            // Run after a short delay to ensure DOM is ready
            setTimeout(updateActiveSection, 100);
        </script>
    </body>
</html>
'''

# Feature cards data with detailed descriptions
FEATURES_DATA = {
    'ml-predictor': {
        'icon': '🤖',
        'title': 'ML Lap Predictor',
        'short': 'RandomForest model with 98% accuracy. Predicts lap times based on tire degradation, fuel load, and track conditions.',
        'detailed': '''
        **Machine Learning Lap Time Prediction**
        
        **Algorithm:** RandomForestRegressor with 100 estimators
        
        **Features (12 dimensions):**
        • Tire age and compound (SOFT/MEDIUM/HARD)
        • Fuel load estimation (decreases by ~0.8kg per lap)
        • Track temperature and air temperature
        • Lap number and race position
        • Gap to leader and traffic density
        • DRS availability and sector times
        
        **Training:**
        • Dataset: 10,000+ historical laps from 2023-2024
        • Train/Test Split: 80/20 with stratified sampling
        • Cross-validation: 5-fold CV with MAE scoring
        
        **Performance Metrics:**
        • R² Score: 0.985 (98.5% variance explained)
        • MAE: 0.12 seconds
        • RMSE: 0.18 seconds
        
        **Real-time Application:**
        Predicts lap times for all 20 drivers every 2 seconds, accounting for tire degradation,
        fuel burn, and changing track conditions. Used for race strategy optimization and
        pit stop timing decisions.
        '''
    },
    'monte-carlo': {
        'icon': '🎲',
        'title': 'Monte Carlo Simulator',
        'short': 'Run 1000+ race scenarios in seconds. Statistical analysis with confidence intervals and win probability calculations.',
        'detailed': '''
        **Monte Carlo Race Simulation**
        
        **Algorithm:** Probabilistic simulation with 1000+ iterations
        
        **Formula:**
        Race Time = Σ(Lap Time + Pit Stop Time + Safety Car Time)
        
        Where:
        • Lap Time ~ N(μ_predicted, σ²_variance)
        • Pit Stop Time ~ N(2.5s, 0.3²)
        • Safety Car Probability = track_factor × lap_progress
        
        **Simulation Process:**
        1. Generate 1000 race scenarios with random variations
        2. Apply tire degradation models (0.05s per lap)
        3. Simulate pit stop strategies (1-stop, 2-stop, 3-stop)
        4. Calculate safety car probabilities (Poisson process)
        5. Aggregate results for statistical analysis
        
        **Statistical Outputs:**
        • Win Probability: P(Position = 1)
        • Podium Probability: P(Position ≤ 3)
        • Expected Position: E[Position]
        • 95% Confidence Interval: [P5, P95]
        • Risk Assessment: σ(Position)
        
        **Performance:**
        • 1000 simulations in <2 seconds
        • Real-time strategy updates
        • Confidence-based decision making
        '''
    },
    'safety-car': {
        'icon': '🚨',
        'title': 'Safety Car Model',
        'short': 'Track-specific probability modeling. Predicts SC/VSC deployment and calculates strategic pit windows.',
        'detailed': '''
        **Safety Car Probability Model**
        
        **Algorithm:** Poisson process with track-specific parameters
        
        **Formula:**
        P(SC) = 1 - e^(-λt)
        
        Where:
        • λ = base_rate × track_factor × weather_factor
        • t = race_progress (0 to 1)
        • base_rate = 0.25 (historical average)
        
        **Track Factors:**
        • Monaco: 2.0 (high probability)
        • Singapore: 1.8
        • Baku: 1.6
        • Monza: 0.5 (low probability)
        • Spa: 0.7
        
        **Strategic Applications:**
        1. Pit Window Optimization: Identify optimal laps for pit stops
        2. Tire Strategy: Adjust compound selection based on SC probability
        3. Risk Management: Calculate expected time loss/gain
        4. Position Prediction: Simulate SC deployment scenarios
        
        **Historical Accuracy:**
        • 78% correct SC predictions (2023 season)
        • 85% correct VSC predictions
        • Average prediction lead time: 5-8 laps
        '''
    },
    'live-telemetry': {
        'icon': '📊',
        'title': 'Live Telemetry',
        'short': 'Real-time race data streaming. Track positions, lap times, tire degradation, and pit stops as they happen.',
        'detailed': '''
        **Real-Time Telemetry System**
        
        **Data Sources:**
        • OpenF1 API - Official F1 timing data
        • FastF1 - Historical race data
        • Custom telemetry simulator for testing
        
        **Update Frequency:**
        • Position updates: Every 2 seconds
        • Lap times: Real-time on lap completion
        • Sector times: Real-time per sector
        • Tire data: Continuous tracking
        
        **Tracked Metrics (per driver):**
        • Current position and gap to leader
        • Lap times (current, best, average)
        • Tire compound and age
        • Pit stop count and timing
        • DRS availability
        • Speed traps and sector times
        
        **Data Processing:**
        • Latency: <10ms from API to dashboard
        • Data validation and anomaly detection
        • Missing data interpolation
        • Real-time aggregation and statistics
        
        **Visualization:**
        • Live track map with car positions
        • Gap analysis charts
        • Tire strategy matrix
        • Sector performance heatmap
        '''
    },
    'track-viz': {
        'icon': '🗺️',
        'title': 'Track Visualization',
        'short': 'Interactive track maps with live car positions. Sector analysis and position change tracking.',
        'detailed': '''
        **Interactive Track Visualization**
        
        **Features:**
        • Real-time car position tracking (all 20 drivers)
        • Animated movement between updates
        • Color-coded by team
        • Position change indicators (↑↓)
        
        **Track Maps:**
        • 24 official F1 circuits
        • Accurate corner and sector boundaries
        • DRS zones highlighted
        • Pit lane entry/exit markers
        
        **Sector Analysis:**
        • S1, S2, S3 time comparison
        • Personal best vs session best
        • Heatmap visualization
        • Micro-sector analysis (100m intervals)
        
        **Position Tracking:**
        • Overtake detection and logging
        • Battle tracking (cars within 1 second)
        • Position history over race
        • Gap evolution charts
        
        **Technical Implementation:**
        • Plotly.js for interactive charts
        • SVG-based track rendering
        • WebSocket for real-time updates
        • Smooth animations with CSS transitions
        '''
    },
    'race-finish': {
        'icon': '⚡',
        'title': 'Race Finish Logic',
        'short': 'Complete race lifecycle management. Final classification, frozen telemetry, and restart capabilities.',
        'detailed': '''
        **Race Lifecycle Management**
        
        **Race States:**
        1. Pre-Race: Setup and initialization
        2. Formation Lap: Grid positions locked
        3. Racing: Live updates every 2 seconds
        4. Finished: Telemetry frozen, report generated
        5. Post-Race: Analysis and statistics
        
        **Finish Detection:**
        • Automatic detection when lap 57/57 reached
        • Leader crosses finish line validation
        • Final classification calculation
        • Interval times locked
        
        **Data Freezing:**
        • All telemetry updates stop
        • Final positions preserved
        • Lap times and gaps frozen
        • Charts remain interactive but static
        
        **Post-Race Report:**
        • Podium finishers (🥇🥈🥉)
        • Race statistics (overtakes, pit stops, DNFs)
        • Key moments timeline
        • Driver performance analysis
        • Championship impact calculation
        
        **Restart Capability:**
        • Reset all race data
        • Reinitialize driver positions
        • Clear historical data
        • Start new race simulation
        '''
    }
}

# Tech stack data with detailed descriptions
TECH_DATA = {
    'python': {
        'icon': '🐍',
        'name': 'Python 3.11+',
        'description': '''
**Core Programming Language**

**Primary Uses:**
• Backend application logic and orchestration
• Data processing pipelines and ETL operations
• Machine learning model implementation
• API integration and data streaming
• Asynchronous task management

**Key Libraries:**
• asyncio - Asynchronous I/O operations
• typing - Type hints for code safety
• dataclasses - Structured data containers
• logging - Application monitoring

**Why Python:**
• Rich ecosystem for data science and ML
• Excellent performance with NumPy/Pandas
• Easy integration with F1 APIs
• Rapid development and prototyping
        '''
    },
    'sklearn': {
        'icon': '🤖',
        'name': 'Scikit-learn',
        'description': '''
**Machine Learning Framework**

**Models Implemented:**
• RandomForestRegressor - Lap time prediction
• Cross-validation - Model evaluation
• GridSearchCV - Hyperparameter tuning
• Feature scaling and normalization

**Training Pipeline:**
• Data preprocessing and cleaning
• Feature engineering (12 dimensions)
• Train/test split (80/20)
• 5-fold cross-validation
• Model persistence and versioning

**Performance:**
• R² Score: 0.985 (98.5% accuracy)
• MAE: 0.12 seconds
• Training time: <5 minutes
• Prediction latency: <1ms per driver
        '''
    },
    'dash': {
        'icon': '📊',
        'name': 'Plotly Dash',
        'description': '''
**Interactive Web Framework**

**Dashboard Components:**
• Real-time chart updates (2-second intervals)
• Interactive Plotly graphs and heatmaps
• Responsive grid layout system
• Modal dialogs and popups
• Custom CSS animations

**Features:**
• Server-side callbacks for data updates
• Client-side callbacks for UI interactions
• WebSocket support for live streaming
• Component state management
• Mobile-responsive design

**Performance:**
• <10ms update latency
• Handles 20+ simultaneous data streams
• Smooth 60fps animations
        '''
    },
    'numpy': {
        'icon': '🔢',
        'name': 'NumPy',
        'description': '''
**Numerical Computing Library**

**Monte Carlo Simulation:**
• Generate 1000+ race scenarios
• Random number generation with seed control
• Statistical distributions (Normal, Poisson)
• Vectorized operations for speed

**Mathematical Operations:**
• Matrix operations for data transformation
• Linear algebra for predictions
• Statistical functions (mean, std, percentiles)
• Array broadcasting for efficiency

**Performance:**
• 100x faster than pure Python loops
• Optimized C/Fortran backend
• Memory-efficient array storage
• SIMD vectorization support
        '''
    },
    'pandas': {
        'icon': '🐼',
        'name': 'Pandas',
        'description': '''
**Data Manipulation Library**

**Telemetry Processing:**
• DataFrame operations for lap data
• Time-series analysis and resampling
• Groupby aggregations for statistics
• Missing data interpolation
• Rolling window calculations

**Feature Engineering:**
• Tire degradation calculations
• Fuel load estimation
• Gap analysis and position tracking
• Sector time comparisons
• Pit stop strategy analysis

**Data Pipeline:**
• CSV/JSON data loading
• Real-time data streaming
• Data validation and cleaning
• Export to multiple formats
        '''
    },
    'fastf1': {
        'icon': '🏎️',
        'name': 'FastF1',
        'description': '''
**F1 Data API**

**Historical Data Access:**
• Race results and lap times (2018-2024)
• Telemetry data (speed, throttle, brake, gear)
• Session information (practice, qualifying, race)
• Weather conditions and track status
• Pit stop timing and tire strategies

**Data Retrieval:**
• Ergast API integration
• FIA timing data parsing
• Track map coordinates
• Driver and team information
• Championship standings

**Use Cases:**
• ML model training data
• Historical performance analysis
• Strategy optimization
• Benchmark comparisons
        '''
    },
    'openf1': {
        'icon': '🔴',
        'name': 'OpenF1 API',
        'description': '''
**Live Timing Data Stream**

**Real-Time Updates:**
• Car positions every 2 seconds
• Lap times and sector splits
• Tire compound and age tracking
• Pit stop detection
• DRS availability status

**Data Streams:**
• Position updates (all 20 drivers)
• Gap analysis to leader/ahead
• Speed trap measurements
• Radio messages
• Race control notifications

**Integration:**
• WebSocket connections
• REST API endpoints
• JSON data format
• <10ms latency
• Automatic reconnection
        '''
    },
    'react': {
        'icon': '⚛️',
        'name': 'React/JavaScript',
        'description': '''
**Frontend Framework**

**Dash Integration:**
• React components power Dash UI
• Virtual DOM for efficient updates
• Component lifecycle management
• State management with hooks
• Event handling and callbacks

**Interactive Features:**
• Smooth CSS transitions
• Hover effects and animations
• Modal dialogs and overlays
• Responsive grid layouts
• Touch-friendly mobile UI

**Performance:**
• 60fps smooth animations
• Lazy loading for optimization
• Code splitting for faster loads
• Browser caching strategies
• Progressive web app support
        '''
    }
}

# Top Title Bar
top_title = html.Div([
    html.Div([
        html.Span("🏎️", style={'fontSize': '24px', 'marginRight': '10px'}),
        html.Span("F1 Strategy Suite", style={
            'fontWeight': '700',
            'fontSize': '18px',
            'color': COLORS['primary'],
            'letterSpacing': '0.5px'
        })
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
], className='top-title')

# macOS-style Dock Navigation (Bottom)
navbar = html.Div([
    html.Div([
        # Navigation Links - Text only, no emojis
        html.A("Home", href='#home', id='nav-home', className='nav-link'),
        html.A("Features", href='#features', id='nav-features', className='nav-link'),
        html.A("Tech Stack", href='#tech-stack', id='nav-tech-stack', className='nav-link'),
        html.A("Dashboard", href='http://localhost:8050', target='_blank', className='nav-link'),
        html.A("About", href='#about', id='nav-about', className='nav-link'),
        
    ], style={'display': 'flex', 'alignItems': 'center', 'gap': '6px'})
], className='navbar', id='navbar')

# Hero Section
hero = html.Div([
    # Speed lines animation
    html.Div([
        html.Div(className='speed-line'),
        html.Div(className='speed-line'),
        html.Div(className='speed-line'),
        html.Div(className='speed-line'),
    ], className='speed-lines'),
    
    html.Div([
        # Badge
        html.Div([
            html.Span("🏎️ PROFESSIONAL EDITION", style={
                'background': 'linear-gradient(90deg, rgba(0,217,255,0.1) 0%, rgba(16,185,129,0.1) 100%)',
                'border': f'1px solid {COLORS["primary"]}',
                'borderRadius': '20px',
                'padding': '8px 20px',
                'fontSize': '12px',
                'fontWeight': '600',
                'color': COLORS['primary'],
                'letterSpacing': '1px'
            })
        ], style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        # Main heading
        html.H1([
            "The Open Source ",
            html.Span("F1 Strategy", style={'color': COLORS['primary']}),
            html.Br(),
            "Intelligence Suite"
        ], style={
            'fontSize': '48px',
            'fontWeight': '800',
            'lineHeight': '1.3',
            'textAlign': 'center',
            'marginBottom': '30px',
            'padding': '0 30px',
            'background': 'linear-gradient(135deg, #E5E7EB 0%, #9CA3AF 100%)',
            'WebkitBackgroundClip': 'text',
            'WebkitTextFillColor': 'transparent',
            'wordWrap': 'break-word',
            'maxWidth': '1000px',
            'margin': '0 auto 30px'
        }),
        
        # Subtitle
        html.P(
            "Real-time race strategy optimization powered by machine learning, Monte Carlo simulation, and advanced telemetry analysis.",
            style={
                'fontSize': '20px',
                'color': COLORS['text_secondary'],
                'textAlign': 'center',
                'maxWidth': '700px',
                'margin': '0 auto 40px',
                'lineHeight': '1.6'
            }
        ),
        
        # CTA Button - Using raw HTML with high z-index
        html.Div([
            html.Form([
                html.Button("Launch Dashboard →", 
                    type='submit',
                    style={
                        'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%)',
                        'border': 'none',
                        'padding': '16px 40px',
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'borderRadius': '8px',
                        'color': '#000',
                        'cursor': 'pointer',
                        'transition': 'all 0.2s',
                        'position': 'relative',
                        'zIndex': '9999'
                    }
                )
            ], action='http://localhost:8050', method='get', target='_blank', style={'position': 'relative', 'zIndex': '9999'})
        ], style={'textAlign': 'center', 'marginBottom': '60px', 'position': 'relative', 'zIndex': '9999'}),
        
        # Stats
        html.Div([
            html.Div([
                html.H3("98%", style={'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['primary'], 'marginBottom': '5px'}),
                html.P("ML Accuracy", style={'fontSize': '14px', 'color': COLORS['text_secondary']})
            ], style={'flex': '1', 'textAlign': 'center'}),
            html.Div([
                html.H3("1000+", style={'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['secondary'], 'marginBottom': '5px'}),
                html.P("Simulations/sec", style={'fontSize': '14px', 'color': COLORS['text_secondary']})
            ], style={'flex': '1', 'textAlign': 'center'}),
            html.Div([
                html.H3("<10ms", style={'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['warning'], 'marginBottom': '5px'}),
                html.P("Update Latency", style={'fontSize': '14px', 'color': COLORS['text_secondary']})
            ], style={'flex': '1', 'textAlign': 'center'}),
        ], style={'display': 'flex', 'gap': '40px', 'maxWidth': '600px', 'margin': '0 auto'})
        
    ], style={
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '100px 40px'
    })
], style={
    'background': f'radial-gradient(circle at 50% 0%, rgba(0,217,255,0.1) 0%, {COLORS["background"]} 50%)',
    'borderBottom': f'1px solid {COLORS["border"]}',
    'paddingTop': '80px'  # Add padding for navbar
})

# Features Section with clickable cards
features = html.Div([
    html.Div([
        html.H2("🚀 Core Features", style={
            'fontSize': '48px',
            'fontWeight': '700',
            'textAlign': 'center',
            'marginBottom': '20px',
            'color': COLORS['text']
        }),
        html.P("Click any card to learn more about the technology", style={
            'fontSize': '18px',
            'color': COLORS['text_secondary'],
            'textAlign': 'center',
            'marginBottom': '60px'
        }),
        
        # Feature Grid with clickable cards
        html.Div([
            # Generate cards from FEATURES_DATA
            html.Div([
                html.Div(FEATURES_DATA['ml-predictor']['icon'], style={'fontSize': '48px', 'marginBottom': '20px'}),
                html.H3(FEATURES_DATA['ml-predictor']['title'], style={'fontSize': '24px', 'fontWeight': '600', 'marginBottom': '15px', 'color': COLORS['text']}),
                html.P(FEATURES_DATA['ml-predictor']['short'],
                       style={'fontSize': '16px', 'color': COLORS['text_secondary'], 'lineHeight': '1.6'}),
                html.Div("Click to expand →", style={'fontSize': '14px', 'color': COLORS['primary'], 'marginTop': '15px', 'fontWeight': '600'})
            ], id='card-ml-predictor', className='feature-card', n_clicks=0, style={
                'background': COLORS['card'],
                'padding': '40px',
                'borderRadius': '12px',
                'border': f'1px solid {COLORS["border"]}'
            }),
            
            html.Div([
                html.Div(FEATURES_DATA['monte-carlo']['icon'], style={'fontSize': '48px', 'marginBottom': '20px'}),
                html.H3(FEATURES_DATA['monte-carlo']['title'], style={'fontSize': '24px', 'fontWeight': '600', 'marginBottom': '15px', 'color': COLORS['text']}),
                html.P(FEATURES_DATA['monte-carlo']['short'],
                       style={'fontSize': '16px', 'color': COLORS['text_secondary'], 'lineHeight': '1.6'}),
                html.Div("Click to expand →", style={'fontSize': '14px', 'color': COLORS['primary'], 'marginTop': '15px', 'fontWeight': '600'})
            ], id='card-monte-carlo', className='feature-card', n_clicks=0, style={
                'background': COLORS['card'],
                'padding': '40px',
                'borderRadius': '12px',
                'border': f'1px solid {COLORS["border"]}'
            }),
            
            html.Div([
                html.Div(FEATURES_DATA['safety-car']['icon'], style={'fontSize': '48px', 'marginBottom': '20px'}),
                html.H3(FEATURES_DATA['safety-car']['title'], style={'fontSize': '24px', 'fontWeight': '600', 'marginBottom': '15px', 'color': COLORS['text']}),
                html.P(FEATURES_DATA['safety-car']['short'],
                       style={'fontSize': '16px', 'color': COLORS['text_secondary'], 'lineHeight': '1.6'}),
                html.Div("Click to expand →", style={'fontSize': '14px', 'color': COLORS['primary'], 'marginTop': '15px', 'fontWeight': '600'})
            ], id='card-safety-car', className='feature-card', n_clicks=0, style={
                'background': COLORS['card'],
                'padding': '40px',
                'borderRadius': '12px',
                'border': f'1px solid {COLORS["border"]}'
            }),
            
            html.Div([
                html.Div(FEATURES_DATA['live-telemetry']['icon'], style={'fontSize': '48px', 'marginBottom': '20px'}),
                html.H3(FEATURES_DATA['live-telemetry']['title'], style={'fontSize': '24px', 'fontWeight': '600', 'marginBottom': '15px', 'color': COLORS['text']}),
                html.P(FEATURES_DATA['live-telemetry']['short'],
                       style={'fontSize': '16px', 'color': COLORS['text_secondary'], 'lineHeight': '1.6'}),
                html.Div("Click to expand →", style={'fontSize': '14px', 'color': COLORS['primary'], 'marginTop': '15px', 'fontWeight': '600'})
            ], id='card-live-telemetry', className='feature-card', n_clicks=0, style={
                'background': COLORS['card'],
                'padding': '40px',
                'borderRadius': '12px',
                'border': f'1px solid {COLORS["border"]}'
            }),
            
            html.Div([
                html.Div(FEATURES_DATA['track-viz']['icon'], style={'fontSize': '48px', 'marginBottom': '20px'}),
                html.H3(FEATURES_DATA['track-viz']['title'], style={'fontSize': '24px', 'fontWeight': '600', 'marginBottom': '15px', 'color': COLORS['text']}),
                html.P(FEATURES_DATA['track-viz']['short'],
                       style={'fontSize': '16px', 'color': COLORS['text_secondary'], 'lineHeight': '1.6'}),
                html.Div("Click to expand →", style={'fontSize': '14px', 'color': COLORS['primary'], 'marginTop': '15px', 'fontWeight': '600'})
            ], id='card-track-viz', className='feature-card', n_clicks=0, style={
                'background': COLORS['card'],
                'padding': '40px',
                'borderRadius': '12px',
                'border': f'1px solid {COLORS["border"]}'
            }),
            
            html.Div([
                html.Div(FEATURES_DATA['race-finish']['icon'], style={'fontSize': '48px', 'marginBottom': '20px'}),
                html.H3(FEATURES_DATA['race-finish']['title'], style={'fontSize': '24px', 'fontWeight': '600', 'marginBottom': '15px', 'color': COLORS['text']}),
                html.P(FEATURES_DATA['race-finish']['short'],
                       style={'fontSize': '16px', 'color': COLORS['text_secondary'], 'lineHeight': '1.6'}),
                html.Div("Click to expand →", style={'fontSize': '14px', 'color': COLORS['primary'], 'marginTop': '15px', 'fontWeight': '600'})
            ], id='card-race-finish', className='feature-card', n_clicks=0, style={
                'background': COLORS['card'],
                'padding': '40px',
                'borderRadius': '12px',
                'border': f'1px solid {COLORS["border"]}'
            }),
            
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(350px, 1fr))',
            'gap': '30px'
        }),
        
        # Modal for expanded card
        html.Div(id='card-modal', children=[], style={'display': 'none'})
        
    ], style={
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '100px 40px'
    })
], style={'background': COLORS['background']})

# Tech Stack Section with glow effects
tech_stack = html.Div([
    html.Div([
        html.H2("🛠️ Technology Stack", style={
            'fontSize': '48px',
            'fontWeight': '700',
            'textAlign': 'center',
            'marginBottom': '20px',
            'color': COLORS['text']
        }),
        html.P("Hover to see what each technology powers", style={
            'fontSize': '18px',
            'color': COLORS['text_secondary'],
            'textAlign': 'center',
            'marginBottom': '60px'
        }),
        
        html.Div([
            # Python
            html.Div([
                html.Div("🐍", style={'fontSize': '56px', 'marginBottom': '15px'}),
                html.P("Python 3.11+", style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text']}),
                html.Div("Click to learn more →", style={'fontSize': '12px', 'color': COLORS['primary'], 'marginTop': '10px', 'fontWeight': '600'})
            ], id='tech-python', className='feature-card', n_clicks=0, style={'textAlign': 'center', 'padding': '40px 30px', 'background': COLORS['card'], 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            
            # Scikit-learn
            html.Div([
                html.Div("🤖", style={'fontSize': '56px', 'marginBottom': '15px'}),
                html.P("Scikit-learn", style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text']}),
                html.Div("Click to learn more →", style={'fontSize': '12px', 'color': COLORS['primary'], 'marginTop': '10px', 'fontWeight': '600'})
            ], id='tech-sklearn', className='feature-card', n_clicks=0, style={'textAlign': 'center', 'padding': '40px 30px', 'background': COLORS['card'], 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            
            # Plotly Dash
            html.Div([
                html.Div("📊", style={'fontSize': '56px', 'marginBottom': '15px'}),
                html.P("Plotly Dash", style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text']}),
                html.Div("Click to learn more →", style={'fontSize': '12px', 'color': COLORS['primary'], 'marginTop': '10px', 'fontWeight': '600'})
            ], id='tech-dash', className='feature-card', n_clicks=0, style={'textAlign': 'center', 'padding': '40px 30px', 'background': COLORS['card'], 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            
            # NumPy
            html.Div([
                html.Div("🔢", style={'fontSize': '56px', 'marginBottom': '15px'}),
                html.P("NumPy", style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text']}),
                html.Div("Click to learn more →", style={'fontSize': '12px', 'color': COLORS['primary'], 'marginTop': '10px', 'fontWeight': '600'})
            ], id='tech-numpy', className='feature-card', n_clicks=0, style={'textAlign': 'center', 'padding': '40px 30px', 'background': COLORS['card'], 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            
            # Pandas
            html.Div([
                html.Div("🐼", style={'fontSize': '56px', 'marginBottom': '15px'}),
                html.P("Pandas", style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text']}),
                html.Div("Click to learn more →", style={'fontSize': '12px', 'color': COLORS['primary'], 'marginTop': '10px', 'fontWeight': '600'})
            ], id='tech-pandas', className='feature-card', n_clicks=0, style={'textAlign': 'center', 'padding': '40px 30px', 'background': COLORS['card'], 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            
            # FastF1
            html.Div([
                html.Div("🏎️", style={'fontSize': '56px', 'marginBottom': '15px'}),
                html.P("FastF1", style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text']}),
                html.Div("Click to learn more →", style={'fontSize': '12px', 'color': COLORS['primary'], 'marginTop': '10px', 'fontWeight': '600'})
            ], id='tech-fastf1', className='feature-card', n_clicks=0, style={'textAlign': 'center', 'padding': '40px 30px', 'background': COLORS['card'], 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            
            # OpenF1
            html.Div([
                html.Div("🔴", style={'fontSize': '56px', 'marginBottom': '15px'}),
                html.P("OpenF1 API", style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text']}),
                html.Div("Click to learn more →", style={'fontSize': '12px', 'color': COLORS['primary'], 'marginTop': '10px', 'fontWeight': '600'})
            ], id='tech-openf1', className='feature-card', n_clicks=0, style={'textAlign': 'center', 'padding': '40px 30px', 'background': COLORS['card'], 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            
            # React/JavaScript
            html.Div([
                html.Div("⚛️", style={'fontSize': '56px', 'marginBottom': '15px'}),
                html.P("React/JS", style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text']}),
                html.Div("Click to learn more →", style={'fontSize': '12px', 'color': COLORS['primary'], 'marginTop': '10px', 'fontWeight': '600'})
            ], id='tech-react', className='feature-card', n_clicks=0, style={'textAlign': 'center', 'padding': '40px 30px', 'background': COLORS['card'], 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(4, 1fr)',
            'gap': '25px',
            'maxWidth': '1200px',
            'margin': '0 auto'
        }),
        
        # Modal for tech details
        html.Div(id='tech-modal', children=[], style={'display': 'none'})
        
    ], style={
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '100px 40px'
    })
], style={'background': COLORS['surface'], 'borderTop': f'1px solid {COLORS["border"]}', 'borderBottom': f'1px solid {COLORS["border"]}'})

# CTA Section
cta = html.Div([
    html.Div([
        html.H2("Ready to optimize your race strategy?", style={
            'fontSize': '48px',
            'fontWeight': '700',
            'textAlign': 'center',
            'marginBottom': '20px',
            'color': COLORS['text']
        }),
        html.P("Start analyzing races with professional-grade tools.", style={
            'fontSize': '20px',
            'color': COLORS['text_secondary'],
            'textAlign': 'center',
            'marginBottom': '40px'
        }),
        html.Div([
            html.Form([
                html.Button("Get Started →",
                    type='submit',
                    style={
                        'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%)',
                        'border': 'none',
                        'padding': '18px 50px',
                        'fontSize': '18px',
                        'fontWeight': '600',
                        'borderRadius': '8px',
                        'color': '#000',
                        'cursor': 'pointer',
                        'transition': 'all 0.2s',
                        'position': 'relative',
                        'zIndex': '9999'
                    }
                )
            ], action='http://localhost:8050', method='get', target='_blank', style={'position': 'relative', 'zIndex': '9999'})
        ], style={'textAlign': 'center', 'position': 'relative', 'zIndex': '9999'})
    ], style={
        'maxWidth': '800px',
        'margin': '0 auto',
        'padding': '100px 40px'
    })
], style={'background': COLORS['background']})

# Footer
footer = html.Div([
    html.Div([
        # Creator info
        html.Div([
            html.H3("Vibhor Joshi", style={
                'fontSize': '28px',
                'fontWeight': '700',
                'color': COLORS['text'],
                'marginBottom': '10px',
                'textAlign': 'center'
            }),
            html.P("Accelerating Insights, Driving Innovation", style={
                'fontSize': '18px',
                'color': COLORS['primary'],
                'marginBottom': '20px',
                'textAlign': 'center',
                'fontWeight': '600'
            }),
            html.P("Data Science | Research | NLP", style={
                'fontSize': '16px',
                'color': COLORS['text_secondary'],
                'marginBottom': '30px',
                'textAlign': 'center'
            }),
        ]),
        
        # Contact links
        html.Div([
            html.A([
                html.Div("💼", style={'fontSize': '24px', 'marginBottom': '8px'}),
                html.P("LinkedIn", style={'fontSize': '14px', 'fontWeight': '600'})
            ], href='https://linkedin.com/in/vibhorjoshi', target='_blank', style={
                'textDecoration': 'none',
                'color': COLORS['text'],
                'padding': '20px 30px',
                'background': COLORS['card'],
                'borderRadius': '10px',
                'border': f'1px solid {COLORS["border"]}',
                'transition': 'all 0.3s',
                'textAlign': 'center',
                'display': 'inline-block',
                'marginRight': '20px'
            }),
            
            html.A([
                html.Div("📧", style={'fontSize': '24px', 'marginBottom': '8px'}),
                html.P("Email", style={'fontSize': '14px', 'fontWeight': '600'})
            ], href='mailto:jvibhor74@gmail.com', style={
                'textDecoration': 'none',
                'color': COLORS['text'],
                'padding': '20px 30px',
                'background': COLORS['card'],
                'borderRadius': '10px',
                'border': f'1px solid {COLORS["border"]}',
                'transition': 'all 0.3s',
                'textAlign': 'center',
                'display': 'inline-block'
            }),
        ], style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        # Copyright
        html.P("© 2025 F1 Strategy Intelligence Suite. Built with ❤️ for F1 fans.", style={
            'textAlign': 'center',
            'color': COLORS['text_secondary'],
            'fontSize': '14px',
            'marginTop': '30px'
        })
    ], style={'padding': '60px 40px', 'maxWidth': '800px', 'margin': '0 auto'})
], style={'background': COLORS['surface'], 'borderTop': f'1px solid {COLORS["border"]}'})

# Layout
app.layout = html.Div([
    # Top Title Bar
    top_title,
    
    # Bottom Dock Navigation
    navbar,
    
    # Global racing waves animation covering entire page
    html.Div([
        html.Div(className='wave wave1'),
        html.Div(className='wave wave2'),
        html.Div(className='wave wave3'),
        html.Div(className='wave wave4'),
    ], className='racing-waves'),
    
    # Content with higher z-index
    html.Div([
        # Home Section
        html.Div(hero, id='home', style={'scrollMarginTop': '80px'}),
        
        # Features Section
        html.Div(features, id='features', style={'scrollMarginTop': '80px'}),
        
        # Tech Stack Section
        html.Div(tech_stack, id='tech-stack', style={'scrollMarginTop': '80px'}),
        
        # CTA Section
        cta,
        
        # About Me Section (Footer)
        html.Div(footer, id='about', style={'scrollMarginTop': '80px'})
    ], style={'position': 'relative', 'zIndex': '1'})
], style={
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh',
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'position': 'relative'
})

# Helper function to parse text with inline bold
def parse_inline_bold(text):
    """Parse text and convert **bold** to actual bold spans"""
    import re
    parts = []
    last_end = 0
    
    # Find all **text** patterns
    for match in re.finditer(r'\*\*(.*?)\*\*', text):
        # Add text before the bold part
        if match.start() > last_end:
            parts.append(html.Span(text[last_end:match.start()]))
        
        # Add bold text
        parts.append(html.Span(match.group(1), style={'fontWeight': '700', 'color': COLORS['primary']}))
        last_end = match.end()
    
    # Add remaining text
    if last_end < len(text):
        parts.append(html.Span(text[last_end:]))
    
    return parts if parts else [html.Span(text)]

# Callback for expandable cards
@callback(
    Output('card-modal', 'style'),
    Output('card-modal', 'children'),
    [Input('card-ml-predictor', 'n_clicks'),
     Input('card-monte-carlo', 'n_clicks'),
     Input('card-safety-car', 'n_clicks'),
     Input('card-live-telemetry', 'n_clicks'),
     Input('card-track-viz', 'n_clicks'),
     Input('card-race-finish', 'n_clicks')],
    prevent_initial_call=True
)
def show_card_details(ml_clicks, mc_clicks, sc_clicks, lt_clicks, tv_clicks, rf_clicks):
    """Show detailed information when a card is clicked"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'display': 'none'}, []
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Map card ID to feature key
    card_map = {
        'card-ml-predictor': 'ml-predictor',
        'card-monte-carlo': 'monte-carlo',
        'card-safety-car': 'safety-car',
        'card-live-telemetry': 'live-telemetry',
        'card-track-viz': 'track-viz',
        'card-race-finish': 'race-finish'
    }
    
    if button_id in card_map:
        feature_key = card_map[button_id]
        feature = FEATURES_DATA[feature_key]
        
        # Create modal content
        modal_content = html.Div([
            # Overlay
            html.Div(id='modal-overlay', className='modal-overlay', n_clicks=0),
            
            # Modal card
            html.Div([
                # Close button
                html.Button("✕", id='close-modal-btn', n_clicks=0, className='close-btn'),
                
                # Content
                html.Div(feature['icon'], style={'fontSize': '72px', 'marginBottom': '25px', 'textAlign': 'center'}),
                html.H2(feature['title'], style={
                    'fontSize': '36px',
                    'fontWeight': '700',
                    'marginBottom': '30px',
                    'color': COLORS['text'],
                    'textAlign': 'center'
                }),
                
                # Detailed description with proper formatting
                html.Div([
                    # Parse and format the detailed text
                    *[
                        html.H3(line.strip().replace('**', ''), style={
                            'fontSize': '24px',
                            'fontWeight': '700',
                            'color': COLORS['primary'],
                            'marginTop': '25px',
                            'marginBottom': '15px',
                            'borderBottom': f'2px solid {COLORS["border"]}',
                            'paddingBottom': '10px'
                        }) if line.strip().startswith('**') and line.strip().endswith('**')
                        else html.Div([
                            html.Span('▸ ', style={'color': COLORS['primary'], 'fontWeight': '700', 'marginRight': '8px'}),
                            *parse_inline_bold(line.strip().replace('• ', ''))
                        ], style={
                            'fontSize': '16px',
                            'marginBottom': '10px',
                            'marginLeft': '20px',
                            'lineHeight': '1.8',
                            'color': COLORS['text']
                        }) if line.strip().startswith('•')
                        else html.P(parse_inline_bold(line.strip()), style={
                            'fontSize': '16px',
                            'color': COLORS['text_secondary'],
                            'marginBottom': '12px',
                            'lineHeight': '1.8'
                        }) if line.strip()
                        else html.Div(style={'height': '15px'})
                        for line in feature['detailed'].strip().split('\n')
                    ]
                ], style={
                    'marginTop': '20px',
                    'maxHeight': '60vh',
                    'overflowY': 'auto',
                    'paddingRight': '15px'
                })
                
            ], className='card-expanded', style={
                'background': COLORS['card'],
                'padding': '50px',
                'borderRadius': '16px',
                'border': f'2px solid {COLORS["primary"]}'
            })
        ])
        
        return {'display': 'block'}, modal_content
    
    return {'display': 'none'}, []

# Callback to close modal
@callback(
    Output('card-modal', 'style', allow_duplicate=True),
    Output('card-modal', 'children', allow_duplicate=True),
    [Input('close-modal-btn', 'n_clicks'),
     Input('modal-overlay', 'n_clicks')],
    prevent_initial_call=True
)
def close_modal(close_clicks, overlay_clicks):
    """Close modal when X button or overlay is clicked"""
    if close_clicks or overlay_clicks:
        return {'display': 'none'}, []
    return dash.no_update, dash.no_update

# Callback for tech stack modals
@callback(
    Output('tech-modal', 'style'),
    Output('tech-modal', 'children'),
    [Input('tech-python', 'n_clicks'),
     Input('tech-sklearn', 'n_clicks'),
     Input('tech-dash', 'n_clicks'),
     Input('tech-numpy', 'n_clicks'),
     Input('tech-pandas', 'n_clicks'),
     Input('tech-fastf1', 'n_clicks'),
     Input('tech-openf1', 'n_clicks'),
     Input('tech-react', 'n_clicks')],
    prevent_initial_call=True
)
def show_tech_details(py_clicks, sk_clicks, dash_clicks, np_clicks, pd_clicks, ff_clicks, of_clicks, react_clicks):
    """Show detailed tech information when clicked"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'display': 'none'}, []
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    tech_map = {
        'tech-python': 'python',
        'tech-sklearn': 'sklearn',
        'tech-dash': 'dash',
        'tech-numpy': 'numpy',
        'tech-pandas': 'pandas',
        'tech-fastf1': 'fastf1',
        'tech-openf1': 'openf1',
        'tech-react': 'react'
    }
    
    if button_id in tech_map:
        tech_key = tech_map[button_id]
        tech = TECH_DATA[tech_key]
        
        modal_content = html.Div([
            html.Div(id='tech-modal-overlay', className='modal-overlay', n_clicks=0),
            html.Div([
                html.Button("✕", id='close-tech-modal-btn', n_clicks=0, className='close-btn'),
                html.Div(tech['icon'], style={'fontSize': '72px', 'marginBottom': '25px', 'textAlign': 'center'}),
                html.H2(tech['name'], style={
                    'fontSize': '36px',
                    'fontWeight': '700',
                    'marginBottom': '30px',
                    'color': COLORS['text'],
                    'textAlign': 'center'
                }),
                html.Div([
                    *[
                        html.H3(line.strip().replace('**', ''), style={
                            'fontSize': '24px',
                            'fontWeight': '700',
                            'color': COLORS['primary'],
                            'marginTop': '25px',
                            'marginBottom': '15px',
                            'borderBottom': f'2px solid {COLORS["border"]}',
                            'paddingBottom': '10px'
                        }) if line.strip().startswith('**') and line.strip().endswith('**')
                        else html.Div([
                            html.Span('▸ ', style={'color': COLORS['primary'], 'fontWeight': '700', 'marginRight': '8px'}),
                            *parse_inline_bold(line.strip().replace('• ', ''))
                        ], style={
                            'fontSize': '16px',
                            'marginBottom': '10px',
                            'marginLeft': '20px',
                            'lineHeight': '1.8',
                            'color': COLORS['text']
                        }) if line.strip().startswith('•')
                        else html.P(parse_inline_bold(line.strip()), style={
                            'fontSize': '16px',
                            'color': COLORS['text_secondary'],
                            'marginBottom': '12px',
                            'lineHeight': '1.8'
                        }) if line.strip()
                        else html.Div(style={'height': '15px'})
                        for line in tech['description'].strip().split('\n')
                    ]
                ], style={
                    'marginTop': '20px',
                    'maxHeight': '60vh',
                    'overflowY': 'auto',
                    'paddingRight': '15px'
                })
            ], className='card-expanded', style={
                'background': COLORS['card'],
                'padding': '50px',
                'borderRadius': '16px',
                'border': f'2px solid {COLORS["primary"]}'
            })
        ])
        
        return {'display': 'block'}, modal_content
    
    return {'display': 'none'}, []

# Close tech modal
@callback(
    Output('tech-modal', 'style', allow_duplicate=True),
    Output('tech-modal', 'children', allow_duplicate=True),
    [Input('close-tech-modal-btn', 'n_clicks'),
     Input('tech-modal-overlay', 'n_clicks')],
    prevent_initial_call=True
)
def close_tech_modal(close_clicks, overlay_clicks):
    if close_clicks or overlay_clicks:
        return {'display': 'none'}, []
    return dash.no_update, dash.no_update

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🏎️  F1 STRATEGY SUITE - LANDING PAGE")
    print("=" * 80)
    print("\n✨ Features:")
    print("   • Interactive cards with glow effects on hover")
    print("   • Click any card to see detailed technical information")
    print("   • Comprehensive project documentation")
    print("   • Beautiful animations and transitions")
    print("   • macOS-style floating dock navigation")
    print("   • Dashboard launch buttons")
    print("\n📍 Landing Page: http://localhost:8051")
    print("📍 Main Dashboard: http://localhost:8050")
    print("\n" + "=" * 80 + "\n")
    
    app.run(debug=True, port=8051)
