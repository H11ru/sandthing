# Powder Game with Rigid Bodies

A 2D particle simulation game featuring both powders and rigid bodies.

## Requirements
- Python 3.8 or higher
- Pygame

## Installation

### For Players
1. Clone the repository:
```bash
git clone https://github.com/yourusername/powder-game.git
cd powder-game
```

2. Install required dependency:
```bash
pip install pygame
```

### For Developers
1. Clone the repository as above

2. Create and activate a virtual environment (recommended):
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install all dependencies including development tools:
```bash
pip install -r requirements.txt
```

4. Run the tests:
```bash
pytest
```

5. Before committing changes:
```bash
# Format code
black .

# Check for style issues
flake8
```

## Running the Game
Run the game using:
```bash
python engine.py
```

If you're using Python 3 explicitly on some systems, use:
```bash
python3 engine.py
```

## System Requirements
- Operating System: Windows, macOS, or Linux
- CPU: Any modern processor (2GHz+ recommended)
- RAM: 512MB minimum, 1GB+ recommended
- Graphics: Any GPU/integrated graphics supporting Pygame
- Screen Resolution: 800x480 minimum

## Troubleshooting

### Game Won't Start
1. Verify Python installation:
```bash
python --version  # Should be 3.8 or higher
```

2. Check Pygame installation:
```bash
python -c "import pygame; print(pygame.version.ver)"
```

3. If you see "pygame not found", reinstall it:
```bash
pip uninstall pygame
pip install pygame
```

### Performance Issues
- Try reducing the number of particles on screen
- Close other applications running in the background
- Update your graphics drivers
- If using a laptop, ensure it's plugged in for better performance

### Controls Not Working
- Check if Caps Lock is on
- Make sure no other application is capturing keyboard input
- Try restarting the game
- Verify you're in the correct mode (Particle/Rigid Body)

For additional help, please create an issue on GitHub.

## Controls

### Particle Mode
- Left Click: Place particles
- Right Click: Erase particles
- Shift + Click: Use larger brush size
- Space: Pause/Resume simulation
- Ctrl+F: Clear screen

### Rigid Body Mode
- TAB: Toggle between Particle/Rigid Body mode
- Left Click: Place or select rigid body
- 1: Cycle through shapes (Box, Ball, Beam, Triangle)
- 2: Cycle through materials (Wood, Metal, Rubber, Crystal)
- G: Toggle gravity for selected rigid body
- Left/Right Arrows: Rotate selected rigid body
- Delete: Remove selected rigid body

## Particles
Various particles with different behaviors:
- Water: Flows and interacts with other particles
- Fire: Rises and spreads
- Sand: Falls and piles up
- And many more...

## Rigid Bodies
Solid objects that maintain their shape:
- Shapes: Box, Ball, Beam, Triangle
- Materials: 
  - Wood (medium density, medium friction)
  - Metal (high density, low friction)
  - Rubber (low density, high friction)
  - Crystal (medium-high density, very low friction)
- Features:
  - Physics-based movement
  - Rotation
  - Material-specific properties
  - Particle displacement
  - Explosion interactions

## Achievement System
Complete various challenges by:
- Using different particles
- Creating reactions
- Building structures
- Triggering explosions