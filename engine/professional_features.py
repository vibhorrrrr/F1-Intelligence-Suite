"""
Professional Features Module
Contains all advanced analytics functions for the F1 dashboard
"""

import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta
from dash import html

def generate_sector_heatmap(drivers, colors):
    """Generate sector performance heatmap"""
    sectors = ['Sector 1', 'Sector 2', 'Sector 3']
    driver_names = [d['name'] for d in drivers[:10]]
    
    # Generate normalized sector performance
    z_data = []
    for driver in drivers[:10]:
        sector_times = [
            90 + np.random.uniform(-5, 5),
            85 + np.random.uniform(-5, 5),
            88 + np.random.uniform(-5, 5)
        ]
        z_data.append(sector_times)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=sectors,
        y=driver_names,
        colorscale='RdYlGn_r',
        showscale=True,
        text=[[f"{val:.1f}s" for val in row] for row in z_data],
        texttemplate="%{text}",
        textfont={"size": 10},
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}s<extra></extra>'
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text'], size=10),
        xaxis=dict(
            side='top',
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=11),
            autorange='reversed'
        ),
        margin=dict(l=50, r=50, t=40, b=10),
        height=300
    )
    
    return fig

def generate_tire_strategy_matrix(drivers, colors, team_colors):
    """Generate tire strategy matrix table"""
    rows = []
    
    for i, driver in enumerate(drivers[:10]):
        # Simulate pit strategy
        if driver['tire_age'] < 15:
            stints = [
                {'compound': 'SOFT', 'laps': 15},
                {'compound': 'MEDIUM', 'laps': 25},
                {'compound': 'HARD', 'laps': 17}
            ]
        else:
            stints = [
                {'compound': 'MEDIUM', 'laps': 20},
                {'compound': 'HARD', 'laps': 37}
            ]
        
        stint_str = " → ".join([f"{s['compound'][:1]}{s['laps']}" for s in stints])
        
        rows.append(
            html.Tr([
                html.Td(f"P{i+1}", style={'fontWeight': '700', 'color': team_colors.get(driver['team'], colors['primary'])}),
                html.Td(driver['name'], style={'fontWeight': '600'}),
                html.Td(stint_str, style={'fontFamily': 'monospace', 'fontSize': '11px'}),
                html.Td(str(len(stints)), style={'textAlign': 'center', 'fontWeight': '600'}),
                html.Td(
                    html.Span(driver['compound'], style={
                        'background': colors['success'] if driver['compound'] == 'SOFT' else colors['warning'] if driver['compound'] == 'MEDIUM' else colors['danger'],
                        'padding': '2px 8px',
                        'borderRadius': '4px',
                        'fontSize': '10px',
                        'fontWeight': '600'
                    })
                )
            ], style={'borderBottom': f'1px solid {colors["border"]}'})
        )
    
    return html.Table([
        html.Thead(
            html.Tr([
                html.Th("Pos", style={'padding': '8px', 'textAlign': 'left'}),
                html.Th("Driver", style={'padding': '8px', 'textAlign': 'left'}),
                html.Th("Strategy", style={'padding': '8px', 'textAlign': 'left'}),
                html.Th("Stops", style={'padding': '8px', 'textAlign': 'center'}),
                html.Th("Current", style={'padding': '8px', 'textAlign': 'left'})
            ], style={'borderBottom': f'2px solid {colors["border"]}', 'color': colors['text_secondary'], 'fontSize': '11px', 'textTransform': 'uppercase'})
        ),
        html.Tbody(rows)
    ], style={'width': '100%', 'fontSize': '12px', 'color': colors['text']})

def check_alerts(drivers, current_lap):
    """Check for alert conditions and return list of alerts"""
    alerts = []
    
    for i, driver in enumerate(drivers[:10]):
        # Tire degradation alert
        if driver['tire_age'] > 25:
            alerts.append({
                'type': 'warning',
                'icon': '⚠️',
                'message': f"{driver['name']} tire age critical ({driver['tire_age']} laps)",
                'driver': driver['name'],
                'timestamp': datetime.now()
            })
        
        # Pit window alert
        if 18 <= current_lap <= 22 and driver['tire_age'] > 15:
            alerts.append({
                'type': 'info',
                'icon': '🔧',
                'message': f"{driver['name']} in optimal pit window",
                'driver': driver['name'],
                'timestamp': datetime.now()
            })
        
        # Gap alert (DRS/overtaking opportunity)
        if i > 0:
            gap = driver['gap_to_leader'] - drivers[i-1]['gap_to_leader']
            if abs(gap) < 1.0:
                alerts.append({
                    'type': 'success',
                    'icon': '🏁',
                    'message': f"{driver['name']} within DRS of {drivers[i-1]['name']} ({abs(gap):.2f}s)",
                    'driver': driver['name'],
                    'timestamp': datetime.now()
                })
    
    return alerts

def generate_weather_report():
    """Generate simulated weather conditions"""
    temp = 28 + np.random.uniform(-2, 2)
    humidity = 45 + np.random.uniform(-5, 5)
    wind_speed = 12 + np.random.uniform(-3, 3)
    rain_chance = max(0, min(100, 15 + np.random.uniform(-10, 10)))
    
    return {
        'track_temp': temp,
        'air_temp': temp - 5,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'wind_direction': 'NE',
        'rain_chance': rain_chance,
        'conditions': 'Dry' if rain_chance < 30 else 'Wet' if rain_chance > 70 else 'Mixed'
    }

def simulate_strategy(driver_name, pit_lap, tire_compound, current_lap, total_laps):
    """Simulate what-if pit stop strategy"""
    # Calculate time loss from pit stop
    pit_time_loss = 22.0  # seconds
    
    # Calculate tire advantage
    laps_remaining = total_laps - pit_lap
    tire_advantage_per_lap = {
        'SOFT': 0.8,
        'MEDIUM': 0.5,
        'HARD': 0.3
    }
    
    tire_advantage = laps_remaining * tire_advantage_per_lap.get(tire_compound, 0.5)
    
    # Net effect
    net_effect = tire_advantage - pit_time_loss
    
    # Determine strategy quality
    if net_effect > 5:
        verdict = "Excellent Strategy"
        color = "success"
        icon = "✅"
    elif net_effect > 0:
        verdict = "Good Strategy"
        color = "success"
        icon = "✅"
    elif net_effect > -5:
        verdict = "Marginal Strategy"
        color = "warning"
        icon = "⚠️"
    else:
        verdict = "Poor Strategy"
        color = "danger"
        icon = "❌"
    
    return {
        'verdict': verdict,
        'color': color,
        'icon': icon,
        'pit_time_loss': pit_time_loss,
        'tire_advantage': tire_advantage,
        'net_effect': net_effect,
        'predicted_position_change': int(net_effect / 3)  # Rough estimate
    }

def generate_race_report(drivers, current_lap, total_laps, driver_names):
    """Generate comprehensive post-race report"""
    if current_lap < total_laps:
        return None
    
    report = {
        'race_info': {
            'date': datetime.now().strftime('%B %d, %Y'),
            'circuit': 'Bahrain International Circuit',
            'laps': total_laps,
            'distance': f'{total_laps * 5.412:.1f} km',
            'duration': '1:32:45.123'
        },
        'podium': [
            {
                'position': 1,
                'driver': driver_names.get(drivers[0]['name'], drivers[0]['name']),
                'team': drivers[0]['team'],
                'time': '1:32:45.123'
            },
            {
                'position': 2,
                'driver': driver_names.get(drivers[1]['name'], drivers[1]['name']),
                'team': drivers[1]['team'],
                'gap': '+5.234s'
            },
            {
                'position': 3,
                'driver': driver_names.get(drivers[2]['name'], drivers[2]['name']),
                'team': drivers[2]['team'],
                'gap': '+12.456s'
            }
        ],
        'fastest_lap': {
            'driver': driver_names.get(drivers[0]['name'], drivers[0]['name']),
            'time': '1:32.456',
            'lap': 45,
            'speed': '215.3 km/h'
        },
        'key_moments': [
            {'lap': 1, 'event': 'Race Start', 'description': f"{driver_names.get(drivers[0]['name'], drivers[0]['name'])} leads into Turn 1"},
            {'lap': 18, 'event': 'Pit Stop', 'description': f"{driver_names.get(drivers[1]['name'], drivers[1]['name'])} pits for MEDIUM tires"},
            {'lap': 23, 'event': 'Overtake', 'description': f"{driver_names.get(drivers[2]['name'], drivers[2]['name'])} passes {driver_names.get(drivers[3]['name'], drivers[3]['name'])} at Turn 4"},
            {'lap': 35, 'event': 'Fastest Lap', 'description': f"{driver_names.get(drivers[0]['name'], drivers[0]['name'])} sets fastest lap: 1:32.456"},
            {'lap': 42, 'event': 'Battle', 'description': f"Intense battle between {driver_names.get(drivers[4]['name'], drivers[4]['name'])} and {driver_names.get(drivers[5]['name'], drivers[5]['name'])}"},
            {'lap': 57, 'event': 'Checkered Flag', 'description': f"{driver_names.get(drivers[0]['name'], drivers[0]['name'])} wins the race!"}
        ],
        'statistics': {
            'total_overtakes': 23,
            'pit_stops': 38,
            'dnf': 2,
            'safety_cars': 0,
            'drs_overtakes': 15,
            'avg_lap_time': '1:34.567',
            'top_speed': '325.4 km/h'
        },
        'driver_of_the_day': driver_names.get(drivers[2]['name'], drivers[2]['name']),
        'team_performance': {
            drivers[0]['team']: 'Excellent',
            drivers[1]['team']: 'Strong',
            drivers[2]['team']: 'Good'
        }
    }
    
    return report
