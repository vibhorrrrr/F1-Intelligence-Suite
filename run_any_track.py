"""
Interactive Track Selector - Simulate any F1 circuit!
"""

import sys
from track_configs import TRACK_DATABASE, get_track_config, list_all_tracks, get_track_info
from engine.sim_engine import F1SimulationEngine

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")

def display_track_menu():
    """Display interactive track selection menu"""
    tracks = list_all_tracks()
    
    print_header("🏎️  F1 STRATEGY SUITE - TRACK SELECTOR  🏎️")
    
    print("Available F1 Circuits:\n")
    
    # Display in columns
    for i, track in enumerate(tracks, 1):
        print(f"  {i:2d}. {track}")
    
    print(f"\n  0. Exit")
    print("\n" + "-"*70)
    
    return tracks

def get_user_choice(tracks):
    """Get track selection from user"""
    while True:
        try:
            choice = input("\nSelect track number (or 0 to exit): ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                sys.exit(0)
            
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(tracks):
                return tracks[choice_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(tracks)}")
        
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

def get_starting_position():
    """Get starting position from user"""
    while True:
        try:
            pos = input("\nStarting grid position (1-20) [default: 8]: ").strip()
            
            if not pos:
                return 8
            
            pos_num = int(pos)
            
            if 1 <= pos_num <= 20:
                return pos_num
            else:
                print("❌ Please enter a position between 1 and 20")
        
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

def get_max_stops():
    """Get maximum pit stops from user"""
    while True:
        try:
            stops = input("\nMaximum pit stops to evaluate (1-3) [default: 2]: ").strip()
            
            if not stops:
                return 2
            
            stops_num = int(stops)
            
            if 1 <= stops_num <= 3:
                return stops_num
            else:
                print("❌ Please enter 1, 2, or 3")
        
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

def simulate_track(track_name, starting_position, max_stops):
    """Run simulation for selected track"""
    
    # Get track configuration
    config = get_track_config(track_name)
    info = get_track_info(track_name)
    
    # Display track info
    print_header(f"SIMULATING: {track_name.upper()}")
    
    print("Track Information:")
    print(f"  Circuit: {info['name']}")
    print(f"  Race Distance: {info['laps']} laps")
    print(f"  Lap Time: {info['lap_time']}")
    print(f"  Track Temperature: {info['temperature']}")
    print(f"  Tire Wear: {info['tire_wear']}")
    print(f"  Overtaking Difficulty: {info['overtaking']}")
    print(f"  DRS Zones: {info['drs_zones']}")
    
    print("\nSimulation Parameters:")
    print(f"  Starting Position: P{starting_position}")
    print(f"  Max Pit Stops: {max_stops}")
    
    print("\n" + "-"*70)
    print("🔄 Running strategy optimization...")
    print("   (This may take 10-20 seconds)")
    print("-"*70 + "\n")
    
    # Initialize engine and optimize
    engine = F1SimulationEngine(config)
    results = engine.optimize_strategy(max_stops=max_stops, starting_position=starting_position)
    
    # Display results
    print_header("OPTIMIZATION RESULTS")
    
    print(f"✅ Analyzed {len(results)} strategies\n")
    
    print("TOP 3 STRATEGIES:\n")
    
    for i, result in enumerate(results[:3], 1):
        print(f"{i}. {result.strategy}")
        print(f"   Total Time: {result.total_race_time:.1f}s ({result.total_race_time/60:.2f} min)")
        print(f"   Final Position: P{result.final_position}")
        print(f"   Position Change: {starting_position - result.final_position:+d}")
        print(f"   Fuel Remaining: {result.fuel_remaining:.1f} kg")
        
        if i == 1:
            print(f"\n   ⭐ OPTIMAL STRATEGY ⭐")
            
            # Show pit stops
            print(f"\n   Pit Stops:")
            for j, stop in enumerate(result.strategy.pit_stops, 1):
                print(f"     Stop {j}: Lap {stop.lap} ({stop.in_compound.value} → {stop.out_compound.value})")
        
        print()
    
    # Ask if user wants to continue
    print("-"*70)
    choice = input("\nSimulate another track? (y/n) [y]: ").strip().lower()
    
    return choice != 'n'

def main():
    """Main interactive loop"""
    
    try:
        while True:
            # Display menu
            tracks = display_track_menu()
            
            # Get user selections
            track_name = get_user_choice(tracks)
            starting_position = get_starting_position()
            max_stops = get_max_stops()
            
            # Run simulation
            continue_sim = simulate_track(track_name, starting_position, max_stops)
            
            if not continue_sim:
                print_header("🏁 THANK YOU FOR USING F1 STRATEGY SUITE!")
                print("For more features, try:")
                print("  • Dashboard: python ui/dashboard_app.py")
                print("  • Jupyter: jupyter notebook analysis/case_study_bahrain.ipynb")
                print("\n")
                break
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
