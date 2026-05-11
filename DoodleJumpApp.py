import math

from .Player import Player
from .Map import Map
from .Constants import PLATFORM_SIZE, CANVAS_SIZE

from app import App
from app_components import clear_background
from system.eventbus import eventbus
from system.scheduler.events import RequestStopAppEvent
from events.input import Buttons, ButtonDownEvent, ButtonUpEvent

TILT_SCALAR_LIMIT = 4


class DoodleJump(App):
    button_states: Buttons
    xyz: tuple[float, float, float]
    y_tilt: float
    cleared: bool
    overlays: list
    player: Player
    map: Map
    scroll_offset: float  # tracks total scroll (camera Y)

    def __init__(self) -> None:
        self.button_states = Buttons(self)
        self.xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.y_tilt = 0.0
        self.cleared = False
        self.overlays = []
        eventbus.on(ButtonDownEvent, self.handle_button_down, self)
        eventbus.on(ButtonUpEvent, self.handle_button_up, self)

        self.player = Player()
        self.map = Map()
        self.scroll_offset = 0.0

    def draw(self, ctx) -> None:
        if not self.cleared:
            clear_background(ctx)
            self.cleared = True
        ctx.save()

        # Background
        ctx.rgb(0, 0.2, 0).rectangle(-120, -120, 240, 240).fill()

        # Draw platforms (center offset + scroll)
        for plat in self.map.platforms:
            plat_screen_x = plat.position.x - CANVAS_SIZE / 2
            plat_draw_y = (
                plat.position.y - self.scroll_offset - CANVAS_SIZE / 2 - PLATFORM_SIZE.y
            )
            ctx.rgb(0, 1, 0).rectangle(
                plat_screen_x,
                plat_draw_y,
                PLATFORM_SIZE.x,
                PLATFORM_SIZE.y,
            ).fill()

        # Draw player (center offset + scroll)
        player_screen_x = self.player.position.x - CANVAS_SIZE / 2
        player_draw_y = self.player.position.y - self.scroll_offset - CANVAS_SIZE / 2
        ctx.rgb(1, 0, 0).arc(
            player_screen_x,
            player_draw_y,
            10,
            0,
            2 * math.pi,
            True,
        ).fill()

        ctx.font = "sans-serif"
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        ctx.font_size = 22
        ctx.rgb(1, 1, 1).move_to(0, -CANVAS_SIZE / 2 + 20).text(
            f"{self.player.score}",
        )

        ctx.restore()

    def update(self, delta: float) -> None:
        """Update game state: player physics, collisions, scrolling."""
        # Update player physics
        self.player.update(delta)

        # Scroll camera to keep player centered in screen-space
        # Screen-space Y is centered at 0, so target is CANVAS_SIZE/2 in logical coords
        player_y = float(self.player.ypos)
        target_scroll = max(0, player_y - (CANVAS_SIZE / 2))
        self.scroll_offset = target_scroll

        # Check collision with platforms
        # Pass scroll offset so Map knows safe recycling zone
        self.map.update(delta, self.scroll_offset)
        self.player.check_platform_collision(self.map.platforms)

    def handle_button_down(self, event: ButtonDownEvent) -> None:
        self.restart()

    def handle_button_up(self, event: ButtonUpEvent) -> None:
        pass

    def quit(self) -> None:
        eventbus.emit(RequestStopAppEvent(self))

    def restart(self) -> None:
        self.player = Player()
        self.map = Map()
        self.scroll_offset = 0.0
        self.cleared = False


__app_export__ = DoodleJump
