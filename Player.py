import time
import math
from .typing import override, TYPE_CHECKING
from imu import acc_read

from .Constants import CANVAS_SIZE, JUMP_VELOCITY, PLATFORM_SIZE, GRAVITY
from .Helpers.XY import XY
from .Protocols.Positionable import Positionable

if TYPE_CHECKING:
    from .Platform import Platform


class Player(Positionable):
    """Doodle Jump-style player with gravity, jumping, and platform detection.

    Player falls under gravity and jumps when landing on a platform.
    Horizontal movement is controlled by device tilt (IMU).
    """

    __canvas_size: int
    __canvas_size_adjusted_for_screen_clipping: int
    __last_time: int
    __xpos: float
    __ypos: float
    __prev_y: float
    __vertical_velocity: float
    __is_jumping: bool
    __is_on_platform: bool
    __score: int
    size: int
    sideways_velocity: float
    response: float
    max_velocity: float

    def __init__(self) -> None:
        self.size = 20
        self.max_velocity = CANVAS_SIZE * 5  # pixels/sec
        self.response = 200.0

        self.__canvas_size = CANVAS_SIZE
        self.__canvas_size_adjusted_for_screen_clipping = CANVAS_SIZE + self.size
        self.__xpos = CANVAS_SIZE / 2.0
        self.__ypos = CANVAS_SIZE / 2  # start at screen center in logical coords
        self.__prev_y = self.__ypos
        self.__last_time = time.ticks_ms()
        self.sideways_velocity: float = 0.0
        self.__vertical_velocity: float = 0.0
        self.__is_jumping: bool = False
        self.__is_on_platform: bool = False
        self.__score = 0

    @property
    def sideways_force(self) -> float:
        return acc_read()[1]

    @property
    def ypos(self) -> float:
        """Vertical position of the player (top-left corner for simplicity)"""
        return self.__ypos

    def is_on_platform(self) -> bool:
        """Check if player is currently on a platform"""
        return self.__is_on_platform

    def check_platform_collision(self, platforms: "set['Platform']") -> bool:
        """Check if player overlaps a platform from above and apply jump

        Only triggers when falling (velocity >= 0). Once jump is triggered,
        player is no longer considered "on platform" until landing again.

        Returns True if a collision was detected (and jump was triggered).
        """
        # Player collision box (simplified: rect from xpos to xpos+size, ypos to ypos+size)
        player_top = self.__ypos
        player_bottom = self.__ypos + self.size
        prev_bottom = self.__prev_y + self.size
        player_left = self.__xpos
        player_right = self.__xpos + self.size

        collided = False
        for plat in platforms:
            px = plat.position.x
            py = plat.position.y
            pw = PLATFORM_SIZE.x
            ph = PLATFORM_SIZE.y

            # Check horizontal overlap
            h_overlap = not (player_right < px or player_left > px + pw)
            # Swept check: bottom crosses platform top between frames
            crossed_from_above = prev_bottom <= py and player_bottom >= py

            # Only trigger jump when falling (downward velocity)
            if h_overlap and crossed_from_above and self.__vertical_velocity >= 0:
                # Landing on platform from above
                collided = True
                self.__is_jumping = True
                # Set player's bottom to platform's top
                self.__ypos = py - self.size
                # Apply jump velocity (upward)
                self.__vertical_velocity = -JUMP_VELOCITY
                # Player is not "on platform" while jumping—only when landing next
                self.__is_on_platform = False
                break

        # Clear platform flag only if not just colliding
        if not collided and self.__vertical_velocity > 0:
            self.__is_on_platform = False

        return collided

    def update(self, delta: float) -> None:
        """Update player physics: horizontal tilt, gravity, and jumping

        delta: time delta in milliseconds.
        """
        now = time.ticks_ms()
        dt_ms = time.ticks_diff(now, self.__last_time)
        self.__last_time = now

        if dt_ms <= 0:
            return

        dt = dt_ms / 1000.0

        # --- Horizontal movement (tilt-based) ---
        tilt = self.sideways_force
        target_velocity = (tilt / GRAVITY) * self.max_velocity
        alpha = 1.0 - math.exp(-self.response * dt)
        self.sideways_velocity += (target_velocity - self.sideways_velocity) * alpha
        self.__xpos = (
            self.__xpos + self.sideways_velocity * dt
        ) % self.__canvas_size_adjusted_for_screen_clipping

        # --- Vertical movement (gravity + jumping) ---
        self.__prev_y = self.__ypos
        # Apply gravity (downward acceleration)
        self.__vertical_velocity += GRAVITY * dt
        self.__ypos += self.__vertical_velocity * dt

        # Clamp horizontal to playfield
        if self.__xpos < 0:
            self.__xpos = 0
        if self.__xpos + self.size > self.__canvas_size:
            self.__xpos = self.__canvas_size - self.size

        self.__update_score(prev_y=self.__prev_y, new_y=self.__ypos)

    def __update_score(self, prev_y: float, new_y: float) -> None:
        """Update score based on vertical progress"""
        self.__score += max(
            0, prev_y - new_y
        )  # Increment score by positive vertical progress

    @property
    def xpos(self) -> int:
        return round(self.__xpos)

    @property
    @override
    def position(self) -> XY:
        return XY(self.xpos, int(round(self.__ypos)))

    @property
    def score(self) -> int:
        return int(self.__score)
