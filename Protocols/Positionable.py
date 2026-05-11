from ..abc import abstractmethod
from ..typing import Protocol
from ..Helpers.XY import XY


class Positionable(Protocol):
    @property
    @abstractmethod
    def position(self) -> XY: ...  # pyright: ignore[reportInvalidAbstractMethod]
