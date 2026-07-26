"""settings.py – static config for in-game variables.

No logic here.
Feel free to experiment with variables.
"""

from pathlib import Path

# --- Paths -------------------------------------------------------------------
# Relative paths to resolve file names
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LEVELS_DIR = BASE_DIR / "levels"

# --- Screen, Timer -----------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# --- Playing Field -------------------------------------------------------------
BRICK_WIDTH, BRICK_HEIGHT = 60, 20
TOP_OFFSET = 60  # Top Offset for UI status bar
FIELD_LEFT = 40  # Left Offset for bricks

# Calculation of the playing field rows and cols
FIELD_COLS = (WIDTH - 2 * FIELD_LEFT) // BRICK_WIDTH
FIELD_RIGHT = FIELD_LEFT + FIELD_COLS * BRICK_WIDTH

# --- Paddle, Ball -----------------------------------------------------------
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 12
PADDLE_SPEED = 7

BALL_RADIUS = 8
BALL_SPEED_X = 4
BALL_SPEED_Y = -5
SLIDE_FACTOR = 0.8
MAX_BALL_SPEED_X = 8

# --- Bonuses ---------------------------------------------------------------------
BONUS_PROBABILITY = 0.3  # Chance that destroyed brick will drop a bonus
BONUS_TYPES = [
    "extend",
    "shrink",
    "multiball",
    "laser",
    "extra_life",
    "speed_up",
    "speed_down",
]
BONUS_SIZE = 24        # Width/height of the falling power-up icon
BONUS_FALL_SPEED = 3   # How fast a power-up falls towards the paddle

# Paddle size effects
PADDLE_EXTEND_STEP = 40   # Pixels added to paddle width by "extend"
PADDLE_SHRINK_STEP = 40   # Pixels removed from paddle width by "shrink"
PADDLE_MIN_WIDTH = 50
PADDLE_MAX_WIDTH = 200

# Ball speed effects
BALL_SPEED_MULTIPLIER = 1.3  # Multiplier applied by speed_up / (1/x) by speed_down
BALL_MIN_SPEED = 2.5
BALL_MAX_SPEED = 12

# Laser bonus
LASER_WIDTH, LASER_HEIGHT = 4, 15
LASER_SPEED = 10
LASER_COOLDOWN = 15  # Frames between shots while the "laser" bonus is active

# Lives
LIVES_START = 3

# --- Visual Effects -----------------------------------------------------------
TRAIL_LENGTH = 6  # Ball's Motion Trail Length
PARTICLE_COUNT = 10  # Particles in brick's burst
PARTICLE_LIFETIME = (12, 24)  # Min/max frames for the particle to live
PARTICLE_SPEED = (1.5, 4.0)  # Min/max particle speed
PARTICLE_GRAVITY = 0.15  # Particle's acceleration
MAX_PARTICLES = 200  # Max particles number

# --- Colors -------------------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PADDLE_COLOR = CYAN
BALL_COLOR = WHITE
BLUE = (60, 140, 255)

# Power-up letter (icon) and color catalog, keyed by BONUS_TYPES entry
BONUS_ICONS = {
    "extend": "E",
    "shrink": "S",
    "multiball": "M",
    "laser": "L",
    "extra_life": "+",
    "speed_up": "F",     # Faster
    "speed_down": "W",   # sloW
}

BONUS_COLORS = {
    "extend": GREEN,
    "shrink": RED,
    "multiball": CYAN,
    "laser": YELLOW,
    "extra_life": MAGENTA,
    "speed_up": ORANGE,
    "speed_down": BLUE,
}

# Brick Color and HP
BRICK_COLORS = {
    2: ORANGE,
    1: RED,
    0: GRAY,         # Indestructible brick
    -1: DARK_GRAY,   # Indestructible level boundaries
}
