from .Platform import Platform
from .Constants import (
    PLATFORM_SIZE,
    CANVAS_SIZE,
    SCROLL_SPEED_PIXELS_PER_SECOND,
    JUMP_HEIGHT,
    SAFETY_PERCENT,
    TARGET_PLATFORMS,
    N_COLS,
)
import random
import math


class Map:
    """Map that generates and maintains platforms using zone-striping and
    column-constrained placement.

    Coordinates: y increases downward. Platforms can have negative y (above
    the top) and are moved down by the scroll speed each update.
    """

    platforms: set[Platform]
    __pixels_gone_down_accumulator: float

    def __init__(self) -> None:
        self.platforms = set()
        self.__pixels_gone_down_accumulator = 0.0
        self._last_col: int = N_COLS // 2
        self._zh: float = JUMP_HEIGHT * SAFETY_PERCENT
        self._populate_initial()

    def zone_height(self) -> float:
        return self._zh

    def zones_on_screen(self) -> int:
        return math.ceil(CANVAS_SIZE / self._zh)

    def plats_per_zone(self) -> int:
        zones_visible = self.zones_on_screen()
        # At least one per zone; if target is lower than zones_visible, clamp it.
        effective_target = max(TARGET_PLATFORMS, zones_visible)
        return max(1, math.ceil(effective_target / zones_visible))

    def _col_range(self, col: int) -> tuple[int, int]:
        cw = CANVAS_SIZE / N_COLS
        lo = int(round(col * cw))
        hi = int(round((col + 1) * cw - PLATFORM_SIZE.x))
        if hi < lo:
            hi = lo
        return lo, hi

    def _generate_platform(self, zone_index: int, prev_col: int | None) -> Platform:
        zh = self.zone_height()
        zone_top = zone_index * zh
        y_min = zone_top + zh * 0.1
        y_max = zone_top + zh * 0.8
        y = int(round(y_min + random.random() * (y_max - y_min)))

        # choose a reachable column (same or adjacent)
        if prev_col is None:
            prev_col = self._last_col
        reachable = [
            c for c in (prev_col - 1, prev_col, prev_col + 1) if 0 <= c < N_COLS
        ]
        col = random.choice(reachable) if reachable else 0
        lo, hi = self._col_range(col)
        x = random.randint(lo, hi)

        p = Platform(x, y, col)
        return p

    def _populate_initial(self) -> None:
        # Fill visible zones and a couple above so scrolling starts full
        zh = self.zone_height()
        zones_visible = self.zones_on_screen()
        extra_above = 2
        # Start at the top of the visible logical space (y=0) since drawing
        # centers the screen; generate extra zones above for upcoming scroll.
        start_zone = 0
        end_zone = zones_visible + extra_above

        col = self._last_col
        for z in range(start_zone, end_zone + 1):
            count = self.plats_per_zone()
            for _ in range(count):
                p = self._generate_platform(z, col)
                self.platforms.add(p)
                col = p.col if p.col is not None else col

    def update(self, dt: float, scroll_offset: float = 0.0) -> None:
        """Advance platforms by scroll amount (dt in ms) and recycle as needed.

        Args:
            dt: time delta in milliseconds
            scroll_offset: current camera scroll (Y coordinate of top of screen).
                Used to determine safe recycling zone.
        """
        pixels_gone_down = dt * (SCROLL_SPEED_PIXELS_PER_SECOND / 1000.0)
        # move all platforms down
        for p in list(self.platforms):
            p.position.y += int(pixels_gone_down)

        # recycle platforms that passed far below the visible area
        # Allow large safety margin so falling player doesn't miss platforms
        zh = self.zone_height()
        recycle_threshold = scroll_offset + CANVAS_SIZE + zh

        # find the currently highest platform (smallest y)
        if not self.platforms:
            return
        highest = min(self.platforms, key=lambda q: q.position.y)
        highest_y = highest.position.y
        prev_col = highest.col if highest.col is not None else self._last_col

        for p in list(self.platforms):
            if p.position.y > recycle_threshold:
                # place into next zone above the current highest platform
                top_zone = math.floor((highest_y - zh) / zh)
                newp = self._generate_platform(top_zone, prev_col)
                # mutate existing object to keep set membership stable
                p.position.x = newp.position.x
                p.position.y = newp.position.y
                p.col = newp.col
                # update highest/prev_col for subsequent recycles
                if p.position.y < highest_y:
                    highest = p
                    highest_y = p.position.y
                prev_col = p.col if p.col is not None else prev_col
