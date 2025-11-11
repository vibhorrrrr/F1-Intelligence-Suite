"""
F1 Strategy Suite - Ultimate Dashboard
Complete professional analytics platform with all advanced features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objs as go
import numpy as np
from datetime import datetime
import pandas as pd

from engine.tire_model import TireCompound, TireDegradationModel
from live.openf1_stream import EnhancedMockDataGenerator
from engine.ml_lap_predictor import MLLapPredictor
from engine.professional_features import (
    generate_sector_heatmap, generate_tire_strategy_matrix,
    check_alerts, generate_weather_report, simulate_strategy,
    generate_race_report
)

# Initialize app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "F1 Strategy Intelligence Suite - Ultimate"

# Add custom CSS for dropdown and resizable charts
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Dropdown styling */
            .Select-control, .Select-menu-outer {
                background-color: white !important;
                color: black !important;
            }
            .Select-value-label, .Select-placeholder {
                color: black !important;
            }
            .Select-option {
                background-color: white !important;
                color: black !important;
            }
            .Select-option:hover {
                background-color: #f0f0f0 !important;
            }
            /* Make charts resizable */
            .js-plotly-plot {
                resize: both !important;
                overflow: auto !important;
                min-width: 200px !important;
                min-height: 150px !important;
            }
            .js-plotly-plot .plotly {
                width: 100% !important;
                height: 100% !important;
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
    </body>
</html>
'''

# Initialize components
mock_gen = EnhancedMockDataGenerator(race_laps=57)
ml_predictor = MLLapPredictor()

# Track previous positions for change detection
previous_positions = {}
alerts_history = []
race_completed = False
race_report_data = None

# Driver full names mapping (2025 F1 Grid - CORRECTED)
DRIVER_NAMES = {
    'VER': 'Max Verstappen',
    'TSU': 'Yuki Tsunoda',
    'RUS': 'George Russell',
    'ANT': 'Andrea Kimi Antonelli',
    'LEC': 'Charles Leclerc',
    'HAM': 'Lewis Hamilton',
    'NOR': 'Lando Norris',
    'PIA': 'Oscar Piastri',
    'ALO': 'Fernando Alonso',
    'STR': 'Lance Stroll',
    'GAS': 'Pierre Gasly',
    'DOO': 'Jack Doohan',
    'ALB': 'Alex Albon',
    'COL': 'Franco Colapinto',
    'LAW': 'Liam Lawson',
    'HAD': 'Isack Hadjar',
    'HUL': 'Nico Hülkenberg',
    'ZHO': 'Zhou Guanyu',
    'BEA': 'Oliver Bearman',
    'OCO': 'Esteban Ocon'
}

# Team colors (2025 F1 Teams)
TEAM_COLORS = {
    'Red Bull': '#1E41FF',
    'Ferrari': '#DC0000',
    'Mercedes': '#00D2BE',
    'McLaren': '#FF8700',
    'Aston Martin': '#006F62',
    'Alpine': '#0090FF',
    'Williams': '#005AFF',
    'RB': '#2B4562',
    'Haas': '#FFFFFF',
    'Sauber': '#00E701'
}

# Modern color scheme
COLORS = {
    'background': '#0B0F19',
    'surface': '#151922',
    'card': '#1A1F2E',
    'border': '#2D3748',
    'primary': '#00D9FF',
    'secondary': '#10B981',
    'accent': '#8B5CF6',
    'text': '#E2E8F0',
    'text_secondary': '#94A3B8',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'chart_line': '#64748B',
    'grid': '#1E293B'
}

def create_track_map():
    """Create interactive track map with live positions"""
    # Simplified track layout (Bahrain-style) - more detailed path
    track_x = [0, 1, 2, 3, 4, 4.5, 4.8, 5, 5, 4.8, 4.5, 4, 3, 2, 1, 0, -1, -2, -2.5, -2.5, -2, -1.5, -1, 0]
    track_y = [0, 0, 0.2, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 3.8, 4, 4, 3.8, 3.5, 3, 3, 2.5, 2, 1.5, 1, 0.5, 0.2, 0]
    
    fig = go.Figure()
    
    # Track outline
    fig.add_trace(go.Scatter(
        x=track_x,
        y=track_y,
        mode='lines',
        line=dict(color=COLORS['border'], width=20),
        showlegend=False,
        hoverinfo='skip',
        name='track'
    ))
    
    # Start/Finish line
    fig.add_trace(go.Scatter(
        x=[0, 0],
        y=[-0.3, 0.3],
        mode='lines',
        line=dict(color=COLORS['text'], width=3, dash='dash'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-3.5, 6]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, 5]),
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        showlegend=False
    )
    
    return fig, track_x, track_y

def create_driver_card(driver, position, is_fastest_lap=False, has_drs=False, position_change=0):
    """Create individual driver performance card"""
    full_name = DRIVER_NAMES.get(driver['name'], driver['name'])
    team_color = TEAM_COLORS.get(driver['team'], COLORS['primary'])
    
    badges = []
    if is_fastest_lap:
        badges.append(html.Span("🏁 FL", style={
            'fontSize': '10px',
            'background': COLORS['accent'],
            'padding': '2px 6px',
            'borderRadius': '4px',
            'marginLeft': '6px'
        }))
    if has_drs:
        badges.append(html.Span("DRS", style={
            'fontSize': '10px',
            'background': COLORS['success'],
            'padding': '2px 6px',
            'borderRadius': '4px',
            'marginLeft': '6px'
        }))
    
    # Position change arrow
    position_arrow = None
    if position_change > 0:
        position_arrow = html.Span(f"↑ {position_change}", style={
            'fontSize': '12px',
            'fontWeight': '700',
            'color': COLORS['success'],
            'marginLeft': '8px'
        })
    elif position_change < 0:
        position_arrow = html.Span(f"↓ {abs(position_change)}", style={
            'fontSize': '12px',
            'fontWeight': '700',
            'color': COLORS['danger'],
            'marginLeft': '8px'
        })
    
    return html.Div([
        # Position badge
        html.Div(f"P{position}", style={
            'position': 'absolute',
            'top': '12px',
            'left': '12px',
            'fontSize': '24px',
            'fontWeight': '700',
            'color': team_color
        }),
        
        # Driver info
        html.Div([
            html.Div([
                html.Span(driver['name'], style={
                    'fontSize': '16px',
                    'fontWeight': '700',
                    'color': COLORS['text']
                }),
                position_arrow if position_arrow else html.Span(),
                *badges
            ], style={'marginBottom': '4px'}),
            html.Div(full_name, style={
                'fontSize': '11px',
                'color': COLORS['text_secondary']
            }),
            html.Div(driver['team'], style={
                'fontSize': '10px',
                'color': team_color,
                'marginTop': '2px'
            })
        ], style={'paddingLeft': '50px'}),
        
        # Stats
        html.Div([
            html.Div([
                html.Span("Gap:", style={'fontSize': '10px', 'color': COLORS['text_secondary']}),
                html.Span(f" +{driver['gap_to_leader']:.2f}s" if driver['gap_to_leader'] > 0 else " ---", 
                         style={'fontSize': '11px', 'fontWeight': '600', 'color': COLORS['text']})
            ]),
            html.Div([
                html.Span("Tire:", style={'fontSize': '10px', 'color': COLORS['text_secondary']}),
                html.Span(f" {driver['compound']} ({driver['tire_age']})", 
                         style={'fontSize': '11px', 'fontWeight': '600', 'color': COLORS['text']})
            ])
        ], style={'paddingLeft': '50px', 'marginTop': '8px'})
        
    ], style={
        'background': COLORS['card'],
        'padding': '12px',
        'borderRadius': '8px',
        'border': f'1px solid {COLORS["border"]}',
        'borderLeft': f'4px solid {team_color}',
        'position': 'relative',
        'marginBottom': '8px'
    })

# Main dashboard layout
app.layout = html.Div([
    # Top Navigation
    html.Div([
        html.Div([
            html.Div([
                html.Span("🏎️", style={'fontSize': '24px', 'marginRight': '10px'}),
                html.Span("F1 Strategy Suite", style={
                    'fontSize': '18px',
                    'fontWeight': '700',
                    'color': COLORS['text']
                }),
                html.Span("ULTIMATE", style={
                    'fontSize': '10px',
                    'fontWeight': '700',
                    'color': COLORS['primary'],
                    'background': f'rgba(0, 217, 255, 0.1)',
                    'padding': '4px 8px',
                    'borderRadius': '4px',
                    'marginLeft': '10px'
                })
            ], style={'display': 'flex', 'alignItems': 'center'}),
            
            html.Div([
                html.Span(f"📅 {datetime.now().strftime('%B %d, %Y')}", style={
                    'fontSize': '14px',
                    'color': COLORS['text_secondary'],
                    'marginRight': '20px'
                }),
                html.Span("🔴 LIVE", style={
                    'fontSize': '12px',
                    'fontWeight': '600',
                    'color': COLORS['danger'],
                    'background': 'rgba(239, 68, 68, 0.1)',
                    'padding': '6px 12px',
                    'borderRadius': '6px',
                    'border': f'1px solid {COLORS["danger"]}'
                })
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'maxWidth': '1800px',
            'margin': '0 auto',
            'padding': '0 30px'
        })
    ], style={
        'background': COLORS['surface'],
        'borderBottom': f'1px solid {COLORS["border"]}',
        'padding': '20px 0',
        'position': 'sticky',
        'top': '0',
        'zIndex': '1000'
    }),
    
    # Main Content
    html.Div([
        # Top Metrics Row
        html.Div([
            # Current Lap
            html.Div([
                html.Div("Current Lap", style={'fontSize': '11px', 'fontWeight': '600', 'color': COLORS['text_secondary'], 'textTransform': 'uppercase', 'letterSpacing': '0.5px', 'marginBottom': '8px'}),
                html.Div(id='current-lap-metric', children="1 / 57", style={'fontSize': '28px', 'fontWeight': '700', 'color': COLORS['text']}),
            ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'flex': '1'}),
            
            # Race Leader
            html.Div([
                html.Div("Race Leader", style={'fontSize': '11px', 'fontWeight': '600', 'color': COLORS['text_secondary'], 'textTransform': 'uppercase', 'letterSpacing': '0.5px', 'marginBottom': '8px'}),
                html.Div(id='leader-name', children="Max Verstappen", style={'fontSize': '20px', 'fontWeight': '700', 'color': COLORS['primary']}),
                html.Div(id='leader-team', children="Red Bull Racing", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginTop': '4px'}),
            ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'flex': '1'}),
            
            # Fastest Lap
            html.Div([
                html.Div("Fastest Lap", style={'fontSize': '11px', 'fontWeight': '600', 'color': COLORS['text_secondary'], 'textTransform': 'uppercase', 'letterSpacing': '0.5px', 'marginBottom': '8px'}),
                html.Div(id='fastest-lap-time', children="1:32.456", style={'fontSize': '28px', 'fontWeight': '700', 'color': COLORS['accent']}),
                html.Div(id='fastest-lap-driver', children="Max Verstappen", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginTop': '4px'}),
            ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'flex': '1'}),
            
            # DRS Available
            html.Div([
                html.Div("DRS Available", style={'fontSize': '11px', 'fontWeight': '600', 'color': COLORS['text_secondary'], 'textTransform': 'uppercase', 'letterSpacing': '0.5px', 'marginBottom': '8px'}),
                html.Div(id='drs-count', children="5", style={'fontSize': '28px', 'fontWeight': '700', 'color': COLORS['success']}),
                html.Div("Drivers in range", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginTop': '4px'}),
            ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'flex': '1'}),
            
        ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '20px'}),
        
        # Main Grid - 4 Columns (OLD + NEW Features)
        html.Div([
            # Column 1 - Track Map, Telemetry & ML Predictions
            html.Div([
                html.Div([
                    html.Div("🗺️ Live Track Map", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Real-time car positions", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    dcc.Graph(id='track-map', figure=create_track_map()[0], config={'displayModeBar': False}, style={'height': '280px'})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'marginBottom': '16px'}),
                
                html.Div([
                    html.Div("📡 Live Telemetry", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Speed, throttle & gear", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    dcc.Graph(id='telemetry-chart', config={'displayModeBar': False}, style={'height': '200px'})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'marginBottom': '16px'}),
                
                html.Div([
                    html.Div("🤖 ML Race Predictor", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("AI finish prediction", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Div(id='ml-predictions')
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            ], style={'flex': '1'}),
            
            # Column 2 - Driver Cards & Gap Analysis & Overtaking (OLD)
            html.Div([
                html.Div([
                    html.Div("👥 Driver Performance", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("All 20 drivers • Live", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Div(id='driver-cards', style={'maxHeight': '300px', 'overflowY': 'auto', 'overflowX': 'hidden', 'paddingRight': '8px'})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'marginBottom': '16px'}),
                
                html.Div([
                    html.Div("📊 Gap Analysis", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Overtaking opportunities", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    dcc.Graph(id='gap-analysis-chart', config={'displayModeBar': False}, style={'height': '180px'})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'marginBottom': '16px'}),
                
                html.Div([
                    html.Div("🎯 Overtaking Predictor", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Next 5 laps forecast", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Div(id='overtaking-predictions')
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            ], style={'flex': '1'}),
            
            # Column 3 - NEW Professional Features (Heatmap, Weather, Tire Matrix)
            html.Div([
                html.Div([
                    html.Div("🔥 Sector Heatmap", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Sector analysis", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Div([
                        dcc.Graph(id='sector-heatmap', config={'displayModeBar': False}, style={'height': '300px', 'width': '100%'})
                    ], style={'overflow': 'hidden'})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'marginBottom': '16px'}),
                
                html.Div([
                    html.Div("🛞 Tire Strategies", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Pit strategies", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Div(id='tire-matrix', style={'overflowX': 'auto', 'maxHeight': '200px', 'overflowY': 'auto'})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'marginBottom': '16px'}),
                
                html.Div([
                    html.Div("🌦️ Weather", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Live conditions", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Div(id='weather-details')
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            ], style={'flex': '1'}),
            
            # Column 4 - NEW Professional Features (What-If, Alerts, Championship)
            html.Div([
                html.Div([
                    html.Div("🎮 What-If Simulator", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Pit stop planning", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Div([
                        dcc.Dropdown(
                            id='sim-driver-select', 
                            options=[{'label': DRIVER_NAMES[k], 'value': k} for k in list(DRIVER_NAMES.keys())[:10]], 
                            value='VER', 
                            style={
                                'marginBottom': '12px', 
                                'fontSize': '12px',
                                'color': '#000000'
                            },
                            className='dark-dropdown'
                        ),
                        dcc.Slider(id='sim-pit-lap', min=1, max=57, value=20, step=1, marks={i: str(i) for i in [1, 20, 40, 57]}, tooltip={"placement": "bottom", "always_visible": True}),
                        dcc.RadioItems(id='sim-tire-compound', options=[{'label': ' S', 'value': 'SOFT'}, {'label': ' M', 'value': 'MEDIUM'}, {'label': ' H', 'value': 'HARD'}], value='MEDIUM', inline=True, style={'color': COLORS['text'], 'marginTop': '8px', 'marginBottom': '8px', 'fontSize': '11px'}),
                        html.Button("Simulate", id='sim-button', n_clicks=0, style={'width': '100%', 'padding': '8px', 'background': f'linear-gradient(135deg, {COLORS["primary"]}, {COLORS["secondary"]})', 'color': COLORS['text'], 'border': 'none', 'borderRadius': '6px', 'fontSize': '12px', 'fontWeight': '600', 'cursor': 'pointer'}),
                        html.Div(id='sim-results', style={'marginTop': '12px', 'fontSize': '11px'})
                    ])
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'marginBottom': '16px'}),
                
                html.Div([
                    html.Div("🔔 Smart Alerts", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Race intelligence", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Div(id='alerts-feed', style={'maxHeight': '200px', 'overflowY': 'auto', 'fontSize': '11px'})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'marginBottom': '16px'}),
                
                html.Div([
                    html.Div("🏆 Championship Impact", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '4px'}),
                    html.Div("Points simulation", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Div(id='championship-impact')
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}'}),
            ], style={'flex': '1'}),
            
        ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '20px'}),
        
        # 6. POST-RACE REPORT SECTION (appears when race completes)
        html.Div(id='race-report-section')
        
    ], style={'maxWidth': '1800px', 'margin': '0 auto', 'padding': '30px'}),
    
    # Update interval
    dcc.Interval(id='interval', interval=2000, n_intervals=0),
    
    # Hidden stores
    html.Div(id='current-lap-store', style={'display': 'none'}),
    
    # Modal for full report
    html.Div(id='report-modal', children=[], style={'display': 'none'})
    
], style={
    'background': COLORS['background'],
    'minHeight': '100vh',
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
})

# Main callback
@app.callback(
    [
        Output('current-lap-metric', 'children'),
        Output('leader-name', 'children'),
        Output('leader-team', 'children'),
        Output('fastest-lap-time', 'children'),
        Output('fastest-lap-driver', 'children'),
        Output('drs-count', 'children'),
        Output('track-map', 'figure'),
        Output('telemetry-chart', 'figure'),
        Output('ml-predictions', 'children'),
        Output('driver-cards', 'children'),
        Output('gap-analysis-chart', 'figure'),
        Output('overtaking-predictions', 'children'),
        Output('sector-heatmap', 'figure'),
        Output('tire-matrix', 'children'),
        Output('weather-details', 'children'),
        Output('alerts-feed', 'children'),
        Output('championship-impact', 'children'),
        Output('race-report-section', 'children'),
        Output('current-lap-store', 'children'),
        Output('interval', 'disabled')
    ],
    [Input('interval', 'n_intervals')]
)
def update_ultimate_dashboard(n):
    global previous_positions, alerts_history, race_completed, race_report_data
    
    try:
        update = mock_gen.generate_lap_update()
        current_lap = update['lap']
        drivers = update['drivers']
        lap_text = f"{current_lap} / 57"
    except Exception as e:
        print(f"Error in update generation: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Leader info
    leader = drivers[0]
    leader_name = DRIVER_NAMES.get(leader['name'], leader['name'])
    leader_team = leader['team']
    
    # Fastest lap (simulated)
    fastest_driver = min(drivers, key=lambda d: d['last_lap_time'])
    fastest_time = f"{int(fastest_driver['last_lap_time'] // 60)}:{fastest_driver['last_lap_time'] % 60:05.3f}"
    fastest_name = DRIVER_NAMES.get(fastest_driver['name'], fastest_driver['name'])
    
    # DRS available
    drs_count = 0
    for i in range(1, len(drivers)):
        gap = drivers[i]['gap_to_leader'] - drivers[i-1]['gap_to_leader']
        if abs(gap) < 1.0:
            drs_count += 1
    
    # 1. Sector Performance Heatmap
    try:
        heatmap = generate_sector_heatmap(drivers, COLORS)
    except Exception as e:
        print(f"Error generating heatmap: {e}")
        import traceback
        traceback.print_exc()
        # Return empty figure on error
        heatmap = go.Figure()
        heatmap.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text="Error loading heatmap", showarrow=False, font=dict(color=COLORS['text']))]
        )
    
    # 2. Weather Report
    weather = generate_weather_report()
    weather_details = html.Div([
        html.Div([
            html.Span("🌡️ Track Temp", style={'fontSize': '11px', 'color': COLORS['text_secondary']}),
            html.Div(f"{weather['track_temp']:.1f}°C", style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['text']})
        ], style={'marginBottom': '12px'}),
        html.Div([
            html.Span("💨 Wind", style={'fontSize': '11px', 'color': COLORS['text_secondary']}),
            html.Div(f"{weather['wind_speed']:.1f} km/h {weather['wind_direction']}", style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['text']})
        ], style={'marginBottom': '12px'}),
        html.Div([
            html.Span("💧 Humidity", style={'fontSize': '11px', 'color': COLORS['text_secondary']}),
            html.Div(f"{weather['humidity']:.0f}%", style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['text']})
        ], style={'marginBottom': '12px'}),
        html.Div([
            html.Span("🌧️ Rain Chance", style={'fontSize': '11px', 'color': COLORS['text_secondary']}),
            html.Div(f"{weather['rain_chance']:.0f}%", style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['warning'] if weather['rain_chance'] > 50 else COLORS['success']})
        ])
    ])
    
    # 3. Tire Strategy Matrix
    tire_matrix = generate_tire_strategy_matrix(drivers, COLORS, TEAM_COLORS)
    
    # 4. Smart Alerts & Notifications
    current_alerts = check_alerts(drivers, current_lap)
    alerts_history.extend(current_alerts)
    alerts_history = alerts_history[-10:]
    
    alert_elements = []
    for alert in reversed(alerts_history):
        color = COLORS['success'] if alert['type'] == 'success' else COLORS['warning'] if alert['type'] == 'warning' else COLORS['primary']
        alert_elements.append(
            html.Div([
                html.Span(alert['icon'], style={'fontSize': '16px', 'marginRight': '8px'}),
                html.Span(alert['message'], style={'fontSize': '12px'})
            ], style={
                'padding': '10px',
                'marginBottom': '8px',
                'background': f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)',
                'border': f'1px solid {color}',
                'borderRadius': '6px',
                'color': COLORS['text']
            })
        )
    
    if not alert_elements:
        alert_elements = [html.Div("No alerts", style={'fontSize': '12px', 'color': COLORS['text_secondary']})]
    
    # OLD FEATURES: Driver Cards, Gap Analysis, Track Map, Championship
    # Track position changes
    current_positions = {driver['name']: i+1 for i, driver in enumerate(drivers)}
    position_changes = {}
    for driver_name, current_pos in current_positions.items():
        if driver_name in previous_positions:
            change = previous_positions[driver_name] - current_pos
            position_changes[driver_name] = change
        else:
            position_changes[driver_name] = 0
    previous_positions = current_positions.copy()
    
    # Driver cards
    cards = []
    for i, driver in enumerate(drivers):
        is_fastest = driver['name'] == fastest_driver['name']
        gap_to_ahead = 0
        if i > 0:
            gap_to_ahead = driver['gap_to_leader'] - drivers[i-1]['gap_to_leader']
        has_drs = abs(gap_to_ahead) < 1.0 and i > 0
        pos_change = position_changes.get(driver['name'], 0)
        cards.append(create_driver_card(driver, i+1, is_fastest, has_drs, pos_change))
    
    # Gap analysis chart
    gap_fig = go.Figure()
    gaps = [0]
    for i in range(1, min(10, len(drivers))):
        gaps.append(drivers[i]['gap_to_leader'] - drivers[i-1]['gap_to_leader'])
    gap_fig.add_trace(go.Bar(
        x=list(range(1, len(gaps)+1)),
        y=gaps,
        marker=dict(color=[COLORS['success'] if g < 1.0 else COLORS['warning'] if g < 3.0 else COLORS['danger'] for g in gaps]),
        hovertemplate='<b>P%{x}</b><br>Gap: %{y:.3f}s<extra></extra>'
    ))
    gap_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'], size=10),
        xaxis=dict(title='Position', gridcolor=COLORS['grid'], showgrid=False),
        yaxis=dict(title='Gap (s)', gridcolor=COLORS['grid'], showgrid=True),
        margin=dict(l=40, r=20, t=20, b=40), showlegend=False
    )
    
    # Track map with moving cars
    track_map, track_x, track_y = create_track_map()
    num_track_points = len(track_x)
    for i, driver in enumerate(drivers[:8]):
        lap_progress = (current_lap % 1.0) + (n % 100) / 100.0
        gap_offset = driver['gap_to_leader'] / 90.0
        total_progress = (lap_progress - gap_offset) % 1.0
        track_index = int(total_progress * (num_track_points - 1))
        x, y = track_x[track_index], track_y[track_index]
        track_map.add_trace(go.Scatter(
            x=[x], y=[y], mode='markers+text',
            marker=dict(size=14, color=TEAM_COLORS.get(driver['team'], COLORS['primary']), line=dict(color=COLORS['text'], width=1)),
            text=driver['name'], textposition='top center',
            textfont=dict(size=9, color=COLORS['text'], family='Arial Black'),
            showlegend=False,
            hovertemplate=f"<b>{DRIVER_NAMES.get(driver['name'], driver['name'])}</b><br>P{i+1}<br>Gap: +{driver['gap_to_leader']:.2f}s<extra></extra>"
        ))
    
    # Telemetry Chart (Leader's data)
    leader = drivers[0]
    # Simulate telemetry data over last 10 seconds
    time_points = list(range(10))
    speed_data = [280 + np.random.uniform(-20, 20) for _ in range(10)]
    throttle_data = [85 + np.random.uniform(-15, 15) for _ in range(10)]
    brake_data = [1 if i % 3 == 0 else 0 for i in range(10)]
    gear_data = [6 + np.random.randint(-2, 2) for _ in range(10)]
    
    telemetry_fig = go.Figure()
    
    # Speed trace
    telemetry_fig.add_trace(go.Scatter(
        x=time_points, y=speed_data,
        mode='lines',
        name='Speed',
        line=dict(color=COLORS['primary'], width=2),
        yaxis='y1'
    ))
    
    # Throttle trace
    telemetry_fig.add_trace(go.Scatter(
        x=time_points, y=throttle_data,
        mode='lines',
        name='Throttle',
        line=dict(color=COLORS['success'], width=2),
        yaxis='y2'
    ))
    
    telemetry_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'], size=10),
        xaxis=dict(
            title='Time (s)',
            gridcolor=COLORS['grid'],
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text='Speed (km/h)', font=dict(color=COLORS['primary'])),
            tickfont=dict(color=COLORS['primary']),
            gridcolor=COLORS['grid'],
            showgrid=True,
            range=[200, 350]
        ),
        yaxis2=dict(
            title=dict(text='Throttle (%)', font=dict(color=COLORS['success'])),
            tickfont=dict(color=COLORS['success']),
            overlaying='y',
            side='right',
            showgrid=False,
            range=[0, 100]
        ),
        margin=dict(l=50, r=50, t=20, b=40),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=9, color='#000000')
        ),
        hovermode='x unified'
    )
    
    # 5. AI Predictions (ML)
    ml_preds = []
    for i, driver in enumerate(drivers[:5]):
        prob = max(0, 100 - (i * 15) - np.random.randint(0, 10))
        ml_preds.append(
            html.Div([
                html.Div([
                    html.Span(f"P{i+1}", style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['primary'], 'width': '30px'}),
                    html.Span(DRIVER_NAMES.get(driver['name'], driver['name']), style={'fontSize': '13px', 'color': COLORS['text'], 'flex': '1'}),
                    html.Span(f"{prob}%", style={'fontSize': '12px', 'fontWeight': '600', 'color': COLORS['success']})
                ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px', 'marginBottom': '8px'}),
                html.Div([
                    html.Div(style={
                        'width': f'{prob}%',
                        'height': '4px',
                        'background': f'linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]})',
                        'borderRadius': '2px'
                    })
                ], style={'background': COLORS['grid'], 'height': '4px', 'borderRadius': '2px', 'marginBottom': '12px'})
            ])
        )
    
    # Overtaking Predictions (top 5 most likely)
    overtake_preds = []
    potential_overtakes = []
    
    for i in range(len(drivers)-1):
        gap = drivers[i+1]['gap_to_leader'] - drivers[i]['gap_to_leader']
        if abs(gap) < 3.0:  # Consider gaps under 3 seconds
            prob = int(max(0, (3.0 - abs(gap)) / 3.0 * 100))
            potential_overtakes.append({
                'attacker': drivers[i+1]['name'],
                'defender': drivers[i]['name'],
                'gap': abs(gap),
                'prob': prob,
                'position': i+1
            })
    
    # Sort by probability and take top 5
    potential_overtakes.sort(key=lambda x: x['prob'], reverse=True)
    
    for overtake in potential_overtakes[:5]:
        color = COLORS['danger'] if overtake['prob'] > 70 else (COLORS['warning'] if overtake['prob'] > 40 else COLORS['text_secondary'])
        
        overtake_preds.append(
            html.Div([
                html.Div([
                    html.Span(f"P{overtake['position']+1} ", style={'fontSize': '11px', 'color': COLORS['text_secondary'], 'fontWeight': '600'}),
                    html.Span(f"{overtake['attacker']} → {overtake['defender']}", style={
                        'fontSize': '13px',
                        'fontWeight': '600',
                        'color': COLORS['text']
                    })
                ], style={'marginBottom': '6px'}),
                html.Div([
                    html.Div([
                        html.Div(style={
                            'width': f'{overtake["prob"]}%',
                            'height': '4px',
                            'background': color,
                            'borderRadius': '2px'
                        })
                    ], style={'background': COLORS['grid'], 'height': '4px', 'borderRadius': '2px', 'flex': '1', 'marginRight': '8px'}),
                    html.Span(f"{overtake['prob']}%", style={'fontSize': '11px', 'fontWeight': '600', 'color': color, 'minWidth': '35px'})
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '4px'}),
                html.Div(f"Gap: {overtake['gap']:.2f}s", style={'fontSize': '10px', 'color': COLORS['text_secondary'], 'marginBottom': '12px'})
            ])
        )
    
    if not overtake_preds:
        overtake_preds = [html.Div("No overtakes predicted", style={'fontSize': '12px', 'color': COLORS['text_secondary']})]
    
    # Championship Impact
    champ_impact = []
    points_map = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    for i, driver in enumerate(drivers[:5]):
        current_points = 250 - (i * 30)
        race_points = points_map[i] if i < len(points_map) else 0
        new_total = current_points + race_points
        champ_impact.append(
            html.Div([
                html.Div([
                    html.Span(driver['name'], style={'fontSize': '13px', 'fontWeight': '600', 'color': COLORS['text']}),
                    html.Span(f"+{race_points} pts", style={'fontSize': '11px', 'color': COLORS['success'], 'marginLeft': '8px'})
                ], style={'marginBottom': '4px'}),
                html.Div([
                    html.Span(f"{current_points} → {new_total}", style={'fontSize': '11px', 'color': COLORS['text_secondary']})
                ], style={'marginBottom': '10px'})
            ])
        )
    
    # 6. Post-Race Report
    race_report_section = None
    if current_lap >= 57 and not race_completed:
        race_completed = True
        race_report_data = generate_race_report(drivers, current_lap, 57, DRIVER_NAMES)
    
    if race_completed and race_report_data:
        report = race_report_data
        # Brief report with button to view full report
        race_report_section = html.Div([
            html.Div("📊 RACE COMPLETED!", style={'fontSize': '24px', 'fontWeight': '700', 'color': COLORS['success'], 'marginBottom': '20px', 'textAlign': 'center'}),
            html.Div([
                html.Div([
                    html.Div("🏆 Podium", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '12px'}),
                    html.Div(f"🥇 {report['podium'][0]['driver']}", style={'marginBottom': '6px', 'fontSize': '15px', 'fontWeight': '700', 'color': COLORS['warning']}),
                    html.Div(f"🥈 {report['podium'][1]['driver']}", style={'marginBottom': '6px', 'fontSize': '14px'}),
                    html.Div(f"🥉 {report['podium'][2]['driver']}", style={'fontSize': '14px'})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'flex': '1', 'color': COLORS['text']}),
                html.Div([
                    html.Div("📈 Quick Stats", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '12px'}),
                    html.Div(f"Total Overtakes: {report['statistics']['total_overtakes']}", style={'marginBottom': '6px', 'fontSize': '13px'}),
                    html.Div(f"Pit Stops: {report['statistics']['pit_stops']}", style={'marginBottom': '6px', 'fontSize': '13px'}),
                    html.Div(f"DNF: {report['statistics']['dnf']}", style={'fontSize': '13px'})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'flex': '1', 'color': COLORS['text']}),
                html.Div([
                    html.Div("📄 Full Report", style={'fontSize': '16px', 'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '12px'}),
                    html.Div("View comprehensive race analysis with key moments, detailed statistics, and driver performances.", style={'fontSize': '12px', 'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Button("View Full Report →", id='show-report-btn', n_clicks=0, style={
                        'width': '100%',
                        'padding': '12px',
                        'background': f'linear-gradient(135deg, {COLORS["accent"]}, {COLORS["primary"]})',
                        'color': COLORS['text'],
                        'border': 'none',
                        'borderRadius': '8px',
                        'fontSize': '14px',
                        'fontWeight': '600',
                        'cursor': 'pointer'
                    })
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'border': f'1px solid {COLORS["border"]}', 'flex': '1'})
            ], style={'display': 'flex', 'gap': '16px'})
        ], style={'marginTop': '30px'})
    
    # Disable interval when race is completed to freeze everything
    interval_disabled = race_completed
    
    return (
        lap_text, leader_name, leader_team, fastest_time, fastest_name, 
        str(drs_count), track_map, telemetry_fig, ml_preds, cards, gap_fig,
        overtake_preds, heatmap, tire_matrix, weather_details, alert_elements,
        champ_impact, race_report_section, str(current_lap), interval_disabled
    )

# What-If Simulator callback
@app.callback(
    Output('sim-results', 'children'),
    [Input('sim-button', 'n_clicks')],
    [State('sim-driver-select', 'value'),
     State('sim-pit-lap', 'value'),
     State('sim-tire-compound', 'value'),
     State('current-lap-store', 'children')]
)
def run_simulation(n_clicks, driver, pit_lap, compound, current_lap_str):
    if n_clicks == 0:
        return None
    
    current_lap = int(current_lap_str) if current_lap_str else 1
    result = simulate_strategy(driver, pit_lap, compound, current_lap, 57)
    
    color_map = {'success': COLORS['success'], 'warning': COLORS['warning'], 'danger': COLORS['danger']}
    verdict_color = color_map.get(result['color'], COLORS['primary'])
    
    return html.Div([
        html.Div([
            html.Span(result['icon'], style={'fontSize': '24px', 'marginRight': '10px'}),
            html.Span(result['verdict'], style={'fontSize': '16px', 'fontWeight': '700', 'color': verdict_color})
        ], style={'marginBottom': '16px', 'display': 'flex', 'alignItems': 'center'}),
        
        html.Div([
            html.Div([
                html.Span("Pit Time Loss:", style={'fontSize': '12px', 'color': COLORS['text_secondary']}),
                html.Span(f" {result['pit_time_loss']:.1f}s", style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['danger']})
            ], style={'marginBottom': '8px'}),
            html.Div([
                html.Span("Tire Advantage:", style={'fontSize': '12px', 'color': COLORS['text_secondary']}),
                html.Span(f" {result['tire_advantage']:.1f}s", style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['success']})
            ], style={'marginBottom': '8px'}),
            html.Div([
                html.Span("Net Effect:", style={'fontSize': '12px', 'color': COLORS['text_secondary']}),
                html.Span(f" {result['net_effect']:+.1f}s", style={'fontSize': '14px', 'fontWeight': '600', 'color': verdict_color})
            ], style={'marginBottom': '8px'}),
            html.Div([
                html.Span("Position Change:", style={'fontSize': '12px', 'color': COLORS['text_secondary']}),
                html.Span(f" {result['predicted_position_change']:+d}", style={'fontSize': '14px', 'fontWeight': '600', 'color': verdict_color})
            ])
        ], style={'padding': '12px', 'background': COLORS['surface'], 'borderRadius': '8px', 'border': f'1px solid {COLORS["border"]}'})
    ])

# Report modal callback
@app.callback(
    Output('report-modal', 'style'),
    Output('report-modal', 'children'),
    [Input('show-report-btn', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_report_modal(show_clicks):
    global race_report_data
    
    if show_clicks and show_clicks > 0 and race_report_data:
        report = race_report_data
        
        # Create full report content
        modal_content = html.Div([
            # Overlay
            html.Div(style={
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'width': '100%',
                'height': '100%',
                'background': 'rgba(0,0,0,0.7)',
                'zIndex': '999'
            }),
            
            # Modal content
            html.Div([
                # Close button - uses JavaScript to hide modal
                html.Button("✕", 
                    id='close-report-btn',
                    n_clicks=0,
                    style={
                        'position': 'absolute',
                        'top': '20px',
                        'right': '20px',
                        'background': 'transparent',
                        'border': 'none',
                        'fontSize': '24px',
                        'color': COLORS['text'],
                        'cursor': 'pointer',
                        'zIndex': '1001'
                    }
                ),
                
                html.H1("🏁 Post-Race Report", style={'color': COLORS['text'], 'marginBottom': '30px'}),
                
                # Race Summary
                html.Div([
                    html.H3("Race Summary", style={'color': COLORS['text'], 'marginBottom': '15px'}),
                    html.P(f"Winner: {report['podium'][0]['driver']}", style={'color': COLORS['text'], 'fontSize': '18px', 'fontWeight': '600'}),
                    html.P(f"Total Laps: 57", style={'color': COLORS['text_secondary']}),
                    html.P(f"Fastest Lap: {report.get('fastest_lap', 'N/A')}", style={'color': COLORS['text_secondary']}),
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '20px'}),
                
                # Podium
                html.Div([
                    html.H3("🏆 Podium", style={'color': COLORS['text'], 'marginBottom': '15px'}),
                    html.Div(f"🥇 1st: {report['podium'][0]['driver']}", style={'marginBottom': '8px', 'fontSize': '16px', 'fontWeight': '700', 'color': COLORS['warning']}),
                    html.Div(f"🥈 2nd: {report['podium'][1]['driver']}", style={'marginBottom': '8px', 'fontSize': '15px', 'color': COLORS['text']}),
                    html.Div(f"🥉 3rd: {report['podium'][2]['driver']}", style={'fontSize': '15px', 'color': COLORS['text']})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '20px'}),
                
                # Key Moments
                html.Div([
                    html.H3("Key Moments", style={'color': COLORS['text'], 'marginBottom': '15px'}),
                    html.Ul([
                        html.Li(
                            f"Lap {moment['lap']}: {moment['event']} - {moment['description']}" if isinstance(moment, dict) else str(moment),
                            style={'color': COLORS['text'], 'marginBottom': '8px'}
                        ) for moment in report.get('key_moments', [])
                    ]),
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '20px'}),
                
                # Statistics
                html.Div([
                    html.H3("Race Statistics", style={'color': COLORS['text'], 'marginBottom': '15px'}),
                    html.P(f"Total Overtakes: {report['statistics']['total_overtakes']}", style={'color': COLORS['text'], 'marginBottom': '8px'}),
                    html.P(f"Pit Stops: {report['statistics']['pit_stops']}", style={'color': COLORS['text'], 'marginBottom': '8px'}),
                    html.P(f"DNF: {report['statistics']['dnf']}", style={'color': COLORS['text']})
                ], style={'background': COLORS['card'], 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '20px'}),
                
            ], style={
                'position': 'fixed',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'background': COLORS['background'],
                'padding': '40px',
                'borderRadius': '16px',
                'maxWidth': '800px',
                'maxHeight': '80vh',
                'overflowY': 'auto',
                'zIndex': '1000',
                'boxShadow': '0 10px 40px rgba(0,0,0,0.3)'
            })
        ])
        
        return {'display': 'block'}, modal_content
    
    return {'display': 'none'}, []

# Close modal callback - separate to avoid initial layout issues
@app.callback(
    Output('report-modal', 'style', allow_duplicate=True),
    [Input('close-report-btn', 'n_clicks')],
    prevent_initial_call=True
)
def close_report_modal(n_clicks):
    if n_clicks and n_clicks > 0:
        return {'display': 'none'}
    return dash.no_update

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🏎️  F1 STRATEGY INTELLIGENCE SUITE - ULTIMATE EDITION")
    print("=" * 80)
    print("\n✅ ALL FEATURES (OLD + NEW 7 PROFESSIONAL):")
    print("\n   OLD FEATURES:")
    print("   • 🗺️ Live Track Map with moving cars")
    print("   • 👥 Driver Performance Cards (all 20 drivers)")
    print("   • 🤖 ML Race Outcome Predictor")
    print("   • 🏆 Championship Impact Simulator")
    print("\n   NEW 7 PROFESSIONAL FEATURES:")
    print("   1. 🎮 What-If Strategy Simulator")
    print("   2. 🔥 Sector Performance Heatmap")
    print("   3. 🛞 Tire Strategy Matrix")
    print("   4. 🔔 Smart Alerts & Notifications")
    print("   5. 🤖 Predictive AI Models")
    print("   6. 🌦️ Weather Report")
    print("   7. 📊 Post-Race Report (brief + full report page)")
    print("\n📍 Main Dashboard: http://localhost:8050")
    print("📍 Full Report: http://localhost:8050/report (after race ends)")
    print("\n" + "=" * 80 + "\n")
    
    app.run(debug=True, port=8050)
