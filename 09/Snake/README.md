# Snake Game - Project 09

A classic Snake implementation in Jack for the nand2tetris course. Snake grows when eating food, speed increases with score, and game ends on collision.

## How to Run

```bash
# Compile Jack code to VM files
./nand2tetris/tools/JackCompiler.sh projects/09/Snake

# Run VM Emulator (GUI will open)
./nand2tetris/tools/VMEmulator.sh
```

In VM Emulator: Load Program → Select Snake folder → Run

## Controls

- **Arrow Keys** - Move snake (up, down, left, right)
- **Space** - Pause/resume
- **Q** - Quit game
- **R** - Restart after game over

## Game Files

**`Main.jack`** - Program entry point, creates and runs game

**`Point.jack`** - Simple x,y coordinate class for positions

**`Random.jack`** - Linear Congruential Generator for food placement

**`Food.jack`** - Food management and rendering
- Spawns at random grid-aligned positions
- Draws as outlined box for visibility
- Collision detection with snake head

**`Snake.jack`** - Snake body, movement, and collision logic
- Array-based body with head/tail management
- Growth mechanics when eating food
- Wall and self-collision detection

**`SnakeGame.jack`** - Main game loop and state management
- Input processing and game state
- Score tracking and UI display
- Game over and restart handling

## Game Mechanics

- **Movement**: 8×8 pixel grid-based motion
- **Growth**: Snake extends when eating food
- **Scoring**: +10 points per food, speed increases
- **Collision**: Game ends on wall hit or self-collision
- **Restart**: Play multiple rounds without program restart

## Technical Notes

- **Memory management**: All classes properly dispose resources
- **Efficient rendering**: Only redraws changed areas (head/tail)
- **Grid alignment**: Snake and food use 8×8 pixel squares
- **Clean architecture**: Modular design with separate responsibilities

**Project 09 Requirements Met:**
- Interactive program with user input
- Graphical display and animation
- Modular design with focused classes
- Programming complexity and challenge
