from __future__ import annotations
from abc import abstractmethod
from copy import deepcopy
from functools import total_ordering
from bounded import BoundedInt
from enum import IntEnum, StrEnum, Enum
from typing import Union, Tuple, Protocol, TypeVar, Generic
from contract import Contract

R = 0
C = 1

TupleInt2 = Tuple[int, int]
TupleInt = Tuple[int, ...]

WIDTH = 8
HEIGHT = 8
MAIN_RECT_RAW = (HEIGHT, WIDTH)
MAX_POSITIVE_INT = 10**9

RowInt = BoundedInt.create_bounded_type(0, HEIGHT-1, "RowInt")
ColInt = BoundedInt.create_bounded_type(0, WIDTH-1, "ColInt")
RowIntExt = BoundedInt.create_bounded_type(-HEIGHT, HEIGHT, "RowIntExt")
ColIntExt = BoundedInt.create_bounded_type(-WIDTH, WIDTH, "ColIntExt")
PositiveInt = BoundedInt.create_bounded_type(0, MAX_POSITIVE_INT, "PositiveInt")

BoundedRect = Tuple[RowInt, ColInt]

class Stone(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"

class NonStoneValues(StrEnum):
    EMPTY = "."

StoneFullDict = {item.name: item.value for item in list(Stone) + list(NonStoneValues)}
StoneFull = StrEnum("StoneFull",StoneFullDict)

class EraseMaskBonus(StrEnum):
    ALL = "ALL"
    COL = "COL"
    ROW = "ROW"
    CROSS = "CROSS"
    
class ActionBonus(StrEnum):
    BRUSH = "BRUSH"
    SHUFFLE = "SHUFFLE" 
    SWAP = "SWAP"

BonusTuple =  {item.name: item.value for item in list(EraseMaskBonus) + list(ActionBonus)}
Bonus = StrEnum("Bonus", BonusTuple)

class RCEnum(IntEnum):
    R = 0
    C = 1

_T_bounded_row = TypeVar("_T_bounded_row", bound=BoundedInt)
_T_bounded_col = TypeVar("_T_bounded_col", bound=BoundedInt)

@total_ordering
class RCBounded(Contract, Generic[_T_bounded_row, _T_bounded_col]):
    @Contract.on
    def __init__(self, row: _T_bounded_row, col: _T_bounded_col):
        self.check_pre(row.is_OK and col.is_OK, "row and col must be correct")
        self._row = row
        self._col = col

    @property
    def row(self) -> _T_bounded_row:
        return self._row
    
    @property
    def col(self) -> _T_bounded_col:
        return self._col

    @Contract.on
    def from_raw(self, row: int, col: int):
        r = deepcopy(self._row)
        c = deepcopy(self._col)
        r.value = row
        c.value = col
        self.check_pre(r.is_OK and c.is_OK, "row and col must be in range")
        self._row = r
        self._col = c

    @property
    def raw_repr(self) -> TupleInt2:
        return (self._row.value, self._col.value)
        
    def __add__(self, other: RCBounded[_T_bounded_row, _T_bounded_col]):
        return RCBounded[_T_bounded_row, _T_bounded_col](self._row + other._row, self._col + other._col)

    def __sub__(self, other: RCBounded[_T_bounded_row, _T_bounded_col]):
        return RCBounded[_T_bounded_row, _T_bounded_col](self._row - other._row, self._col - other._col)

    def __eq__(self, other: RCBounded[_T_bounded_row, _T_bounded_col]):
        return self._row == other._row and self._col == other._col

    def __lt__(self, other: self._board.non_empty_cells):
        return self._row < other._row or (self._row == other._row and self._col < other._col)

    def __hash__(self) -> int:
        return hash(self.raw_repr)
    
    def __repr__(self) -> str:
        return f"RCBounded({self._row.value}, {self._col.value})"

    @classmethod
    @abstractmethod
    def create_from_raw(self, rc_raw: TupleInt2) -> RCBounded[_T_bounded_row, _T_bounded_col]:
        pass
    


RC = RCBounded[RowInt, ColInt]
RCExt = RCBounded[RowIntExt, ColIntExt]

class Rect(Contract):
    @Contract.on
    def __init__(self, width: PositiveInt, height: PositiveInt):
        self.check_pre(width.is_OK and height.is_OK)
        self._width = width
        self._height = height

    def __contains__(self, rc: RC) -> bool:
        return (0 <= rc.row.value < self._height.value) and (0 <= rc.col.value < self._width.value)  # Исправлено: использовать .value и свойства

    def __iter__(self):
        for row in range(self._height.value):  # Добавить .value
            for col in range(self._width.value):  # Добавить .value
                yield RC(RowInt(row), ColInt(col))

    @property
    def width(self) -> PositiveInt:
        return self._width

    @property
    def height(self) -> PositiveInt:
        return self._height

    @Contract.on
    def from_raw(self, w: int, h: int):
        w_safe = PositiveInt(w)
        h_safe = PositiveInt(h)
        self.pre_check(w_safe.is_OK and h_safe.is_OK, "Width and height must be positive or zero")
        self._height = h_safe
        self._width = w_safe


MAIN_RECT = Rect(PositiveInt(HEIGHT), PositiveInt(WIDTH))

class PrinterConstants:
    PRINT_STEPS_FLAG = 1
    PRINT_BOARD_FLAG = 2
    PRINT_ALL_MODE = 0xFFFF
    PRINT_NONE_MODE = 0x0000

class Printer(PrinterConstants):
    # декоратор, который печатает первый аргумент у оборачиваемой функции
    # чаще всего это self у методов -- печатает объект после выполнения метода
    # при этом флаги должны соответствовать PRINT_MODE (быть подняты соотвтествующие биты)
    
    MODE = PrinterConstants.PRINT_ALL_MODE
    @classmethod
    def on(cls, message: str, printing_flags: int):
        def decorator(func):
            def wrapper(*args, **kwargs):
                ans = func(*args, **kwargs)
                if cls.MODE & printing_flags != 0:
                    print("\n" + message)
                    if len(args) > 0:
                        print(args[0])
                return ans
            return wrapper
        return decorator

    @classmethod
    def is_steps_on(cls) -> bool:
        return bool(cls.MODE & cls.PRINT_STEPS_FLAG != 0)
    
    @classmethod
    def is_board_on(cls) -> bool:
        return bool(cls.MODE & cls.PRINT_BOARD_FLAG != 0)
    
    @classmethod
    def steps_off(cls):
        cls.MODE &= ~cls.PRINT_STEPS_FLAG

    @classmethod
    def board_off(cls):
        cls.MODE &= ~cls.PRINT_BOARD_FLAG

    @classmethod
    def all_off(cls):
        cls.MODE = cls.PRINT_NONE_MODE
        
    @classmethod
    def all_on(cls):
        cls.MODE = cls.PRINT_ALL_MODE
        
    @classmethod
    def steps_on(cls):
        cls.MODE |= cls.PRINT_STEPS_FLAG

    @classmethod
    def board_on(cls):
        cls.MODE |= cls.PRINT_BOARD_FLAG



        

if __name__ == "__main__": 
    print(Printer.MODE)
    Printer.steps_off()
    print(Printer.MODE)
    Printer.board_off()
    print(Printer.MODE)
    Printer.board_on()
    print(Printer.MODE)
    Printer.steps_on()
    print(Printer.MODE)
    Printer.all_off()
    print(Printer.MODE)
    Printer.all_on()
    print(Printer.MODE)