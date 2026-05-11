from .Helpers.XY import XY


CANVAS_SIZE = 240
# Vertical physics (pixels/sec, pixels/sec^2)
JUMP_VELOCITY = 150  # pixels/sec
GRAVITY = 150.0  # pixels/sec^2
PLATFORM_SIZE: XY = XY(40, 10)
SCROLL_SPEED_PIXELS_PER_SECOND = 100

# Zone/column placement constants (used by new Map generation)
# Max vertical distance (in px) the player can reach in a jump.
# h = v^2 / (2g)
JUMP_HEIGHT = (JUMP_VELOCITY * JUMP_VELOCITY) / (2 * GRAVITY)
# safety margin as fraction of jump height
SAFETY_PERCENT = 0.85
# Target number of platforms to maintain on-screen
TARGET_PLATFORMS = 3
# Number of horizontal columns to divide the playfield into
N_COLS = 3

# Optional: max horizontal reach in px (for column math)
MAX_H_REACH = 160
