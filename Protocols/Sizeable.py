from ..abc import abstractmethod
from ..typing import Protocol
from ..Helpers.XY import XY


class Sizeable(Protocol):
    @property
    @abstractmethod
    def size(self) -> XY: ...  # pyright: ignore[reportInvalidAbstractMethod]
