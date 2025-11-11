# 🚀 Quick Start Guide

## Get Started in 5 Minutes

### 1️⃣ Clone & Install

```bash
# Clone the repository
git clone https://github.com/vibhorjoshi/f1-strategy-suite.git
cd f1-strategy-suite

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Launch the Application

**Option A: One-Click Launch (Windows - Easiest!)**
```bash
# Double-click start.bat or run:
start.bat
```
This will automatically:
- Launch landing page on port 8051
- Launch dashboard on port 8050 (background)
- Open landing page in your browser
- Navigate to dashboard using the buttons on landing page

To stop all servers:
```bash
stop.bat
```

**Option B: Manual Launch - Landing Page**
```bash
python ui/landing_page.py
```
Then open: **http://localhost:8051**

**Option C: Manual Launch - Main Dashboard**
```bash
python ui/ultimate_dashboard.py
```
Then open: **http://localhost:8050**

**Option D: Run Both Manually (Best Experience)**
```bash
# Terminal 1:
python ui/landing_page.py

# Terminal 2:
python ui/ultimate_dashboard.py
```
- Landing Page: **http://localhost:8051**
- Dashboard: **http://localhost:8050**

### 3️⃣ Run a Quick Simulation

```bash
python run_any_track.py
```

Select a track from the menu and watch the simulation run!

---

## 📊 What You'll See

### Landing Page (Port 8051)
- Project overview and features
- Interactive tech stack cards
- macOS-style navigation dock
- Links to main dashboard

### Main Dashboard (Port 8050)
- **Live Race Positions** - Real-time driver standings
- **ML Lap Predictions** - AI-powered lap time forecasts
- **Monte Carlo Simulation** - 1000+ race scenarios
- **Strategy Recommendations** - Optimal pit stop windows
- **Interactive Charts** - Position evolution, tire degradation

---

## 🎯 Common Use Cases

### 1. Analyze a Specific Track
```python
python run_any_track.py
# Choose from 24 F1 circuits
```

### 2. View Real-Time Race Data
```bash
# Start dashboard
python ui/ultimate_dashboard.py

# Dashboard auto-updates every 2 seconds
# Shows live positions, lap times, and predictions
```

### 3. Run Custom Simulation
```python
from engine.sim_engine import F1SimulationEngine, RaceConfig

config = RaceConfig(
    track_name="Monaco",
    race_laps=78,
    base_lap_time=72.0,
    track_temp=28.0
)

engine = F1SimulationEngine(config)
results = engine.optimize_strategy(max_stops=2)
print(results[0].summary())
```

---

## 🔧 Troubleshooting

### Issue: Port Already in Use
```bash
# Kill process on port 8050
# Windows:
netstat -ano | findstr :8050
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8050 | xargs kill -9
```

### Issue: Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Dashboard Not Loading
1. Check Python version: `python --version` (need 3.9+)
2. Check if server is running: Look for "Dash is running on http://..."
3. Clear browser cache and refresh

---

## 📚 Next Steps

1. **Explore the Dashboard** - Try different tracks and strategies
2. **Read the Docs** - Check `docs/architecture.md` for technical details
3. **View Architecture** - See `ARCHITECTURE_PIPELINE.md` for system design
4. **Customize** - Modify `track_configs.py` for custom tracks

---

## 💡 Pro Tips

- **Use Chrome/Firefox** for best dashboard performance
- **Keep both apps running** for full experience
- **Check console output** for simulation details
- **Explore the code** - All modules are well-documented

---

## 🆘 Need Help?

- **Email**: jvibhor74@gmail.com
- **LinkedIn**: [linkedin.com/in/vibhorjoshi](https://linkedin.com/in/vibhorjoshi)
- **GitHub Issues**: [github.com/vibhorjoshi/f1-strategy-suite/issues](https://github.com/vibhorjoshi/f1-strategy-suite/issues)

---

**Happy Racing! 🏎️💨**
