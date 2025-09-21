from enum import StrEnum
from typing import TypedDict, List, Tuple, Dict, Sequence, Collection, Set
from copy import deepcopy
from contract import Contract
from base import HEIGHT, WIDTH, PositiveInt, RowInt, ColInt, ColIntExt, RowIntExt, Bonus, EraseMaskBonus, Rect, MAIN_RECT, RC, RCExt, TupleInt2, MAIN_RECT_RAW

# === ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ ===
RCExtCollection = Collection[RCExt]
RCSet = Set[RC]
DEFAULT_PIVOT = RC(RowInt(0), ColInt(0))
MaskRaw = Tuple[TupleInt2, ...]

class Mask(Contract):
    """Класс для работы с масками координат на игровом поле."""
    @Contract.on
    def __init__(self, rc_set: RCSet = set()):
        """Инициализация маски с точкой привязки и набором координат."""
        self._rect = MAIN_RECT
        self.check_pre(all([rc in self._rect for rc in rc_set]))
        self._rc_set = rc_set
        
     
    def __len__(self):
        return len(self._rc_set)
    
    @property
    def is_empty(self) -> bool:
        return len(self) == 0
    
    def __contains__(self, rc: RC) -> bool:
        return rc in self._rc_set
    
    def __iter__(self):
        return iter(self._rc_set)
    
    def from_rc_ext_collection(self, rc_pivot: RC, rc_ext_collection: RCExtCollection):
        rc_abs_tuple = (rc_pivot + rc_ext for rc_ext in rc_ext_collection)
        self._rc_set = set(filter(lambda rc: rc.is_OK and rc in self._rect, rc_abs_tuple))
        return self
        
    def from_raw(self, pivot_raw: TupleInt2, mask_raw: MaskRaw):
        rc_pivot = RC(RowIntExt(pivot_raw[0]),ColIntExt(pivot_raw[1]))
        rc_ext_collection = [RCExt(RowIntExt(tuple_int2[0]), ColIntExt(tuple_int2[1])) for tuple_int2 in mask_raw]
        rc_ext_collection = filter(lambda rc_ext: rc_ext.is_OK, rc_ext_collection)
        self._rc_set = set(\
            filter(\
                lambda rc: rc.is_OK and rc in self._rect, \
                (rc_pivot + rc_ext for rc_ext in rc_ext_collection)))
        return self
    
    def move(self, delta: RC):
        moved_rc_list = [rc + delta for rc in self._rc_set]
        self._rc_set = set(filter (lambda rc: rc.is_OK, moved_rc_list))
        
    def __str__(self):
        return " ".join(str(rc.raw_repr) for rc in self)
        
COMBINATIONS: Dict[str, MaskRaw] = {
    "T1": ((-2, 0), (-1, 0), (0,0), (1, 0), (2,0), (0,1), (0,2)),
    "T2": ((0, -2), (0, -1), (0,0), (0, 1), (0,2), (1,0), (2,0)),
    "L1": ((0, 2), (0, 1), (0, 0), (1, 0), (2, 0)),
    "L2": ((0, -2), (0, -1), (0,0), (0, 1), (0,2)),
    "L3": ((-2, 0), (-1, 0), (0,0), (0, -1), (0, -2)),
    "L4": ((0, 0), (1, 0), (2, 0), (0, -2), (0, -1)),
    "THREE_1": ((0, 0), (-1, 0), (1, 0)),
    "THREE_2": ((0, 0), (0, -1), (0, 1)),
    "FOUR_1": ((-1, 0), (0, 0), (1, 0), (2, 0)) ,
    "FOUR_2": ((0, -1), (0, 0), (0, 1), (0, 2)),
    "FOUR_3": ((-2, 0), (-1, 0), (0, 0), (1, 0)),
    "FOUR_4":  ((0, -2), (0, -1), (0, 0), (0, 1)),
    "FIVE_1":  ((-1, 0), (0, 0), (1, 0), (2, 0), (3, 0)),
    "FIVE_2": ((0, -1), (0, 0), (0, 1), (0, 2), (0, 3))
}

ERASE_BONUS_MASKS: Dict[EraseMaskBonus, MaskRaw] = {
    EraseMaskBonus.ROW: [(0, col) for col in range(-WIDTH, WIDTH)],  # Вся строка
    EraseMaskBonus.COL: [(row, 0) for row in range(-HEIGHT, HEIGHT)],  # Весь столбец
    EraseMaskBonus.CROSS: [(0, col) for col in range(-WIDTH, WIDTH)] + [(row, 0) for row in range(-HEIGHT, HEIGHT)],  # Весь крест
    EraseMaskBonus.ALL: [(row, col) for row in range(-HEIGHT, HEIGHT) for col in range(-WIDTH, WIDTH)]  # Все ячейки поля
}

if __name__ == "__main__":
        rc_set = {
            RC(RowInt(7), ColInt(7))  # близко к границе
        }
        mask = Mask(rc_set)
        
        # Перемещаем за границы
        delta = RC(RowInt(2), ColInt(2))
        mask.move(delta)
        
        # Координаты за границами должны быть отфильтрованы
        # Проверяем, что маска может стать пустой или содержать только валидные координаты
        for rc in mask._rc_set:
            assert rc.is_OK