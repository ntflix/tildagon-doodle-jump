from .typing import override
from .Constants import PLATFORM_SIZE
from .Protocols.Positionable import Positionable
from .Helpers.XY import XY


class Platform(Positionable):
    """
    - `x`,`y` are in logical canvas coordinates (0..CANVAS_SIZE)
    - Coordinate adjustment for centered screen display happens in drawing
    - `col` is the column index the platform occupies (optional)
    """

    def __init__(self, x: int, y: int, col: int | None = None):
        super().__init__()
        self._position: XY = XY(int(x), int(y))
        self.col: int | None = col
        self.w: int = PLATFORM_SIZE.x
        self.h: int = PLATFORM_SIZE.y

    @property
    @override
    def position(self) -> XY:
        return self._position

    def __repr__(self) -> str:
        return f"Platform(x={self._position.x}, y={self._position.y}, col={self.col})"
