from __future__ import annotations
from abc import ABC, abstractmethod
import random
from typing import TypedDict, Dict
from contract import Contract
from base import (
    PositiveInt, Stone, NonStoneValues, RowInt, ColInt, 
    WIDTH, HEIGHT, Bonus, RC, Rect, R, C, 
    MAIN_RECT, MAIN_RECT_RAW, StoneFull
)

# === ИНТЕРФЕЙСЫ ===

class ICells(Contract):
    """Интерфейс для управления ячейками игрового поля."""
    
    # === ЗАПРОСЫ ===
    @abstractmethod
    def width(self) -> PositiveInt:
        """Возвращает ширину поля."""
        pass
    
    @abstractmethod
    def height(self) -> PositiveInt:
        """Возвращает высоту поля."""
        pass
    
    @abstractmethod
    def rect(self) -> Rect:
        """Возвращает прямоугольник поля."""
        pass
    
    @abstractmethod
    def __getitem__(self, rc: RC) -> Stone:
        'Предусловие: rc находится в пределах поля'
        pass
    
    # === КОМАНДЫ ===
    @abstractmethod
    def __setitem__(self, rc: RC, stone: Stone) -> None:
        """Предусловие: rc находится в пределах поля
        Постусловие: в позиции rc установлен указанный камень
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Очищает все ячейки поля.
        Постусловие: все ячейки равны NonStoneValues.EMPTY
        """
        pass
    
    @abstractmethod
    def erase_rc(self, rc: RC) -> None:
        """Стирает камень в указанной позиции.
        Предусловие: rc находится в пределах поля
        Постусловие: в позиции rc установлен NonStoneValues.EMPTY
        """
        pass


class IBonusChest(ABC):
    """Интерфейс для отслеживания бонусов."""
    
    # === ЗАПРОСЫ ===
    @abstractmethod
    def get_bonus_count(self, bonus: Bonus) -> int:
        """Возвращает количество указанного бонуса.
        
        Постусловие: результат >= 0
        """
        pass
    
    # === КОМАНДЫ ===
    @abstractmethod
    def use_bonus(self, bonus: Bonus) -> None:
        """Использует один бонус указанного типа.
        
        Предусловие: количество бонусов данного типа > 0
        Постусловие: количество бонусов данного типа уменьшено на 1
        """
        pass
    
    @abstractmethod
    def add_bonus(self, bonus: Bonus) -> None:
        """Добавляет один бонус указанного типа.
        
        Постусловие: количество бонусов данного типа увеличено на 1
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Сбрасывает все бонусы до нуля.
        
        Постусловие: количество всех бонусов равно 0
        """
        pass


class IStatistics(ABC):
    """Интерфейс для отслеживания игровой статистики."""
    
    # === ЗАПРОСЫ ===
    @abstractmethod
    def get_scores(self) -> PositiveInt:
        """Возвращает текущее количество очков.
        
        Постусловие: результат >= 0
        """
        pass
    
    @abstractmethod
    def get_used_bonus_count(self, bonus: Bonus) -> PositiveInt:
        """Возвращает количество использований указанного бонуса.
        
        Постусловие: результат >= 0
        """
        pass
    
    # === КОМАНДЫ ===
    @abstractmethod
    def reset(self) -> None:
        """Сбрасывает статистику до начальных значений.
        
        Постусловие: все счетчики равны 0
        """
        pass
    
    @abstractmethod
    def use_bonus(self, bonus: Bonus) -> None:
        """Регистрирует использование бонуса.
        
        Постусловие: счетчик использований данного бонуса увеличен на 1
        """
        pass
    
    @abstractmethod
    def increase_scores(self, count: PositiveInt) -> None:
        """Увеличивает количество очков.
        
        Предусловие: count > 0
        Постусловие: очки увеличены на count
        """
        pass

# === РЕАЛИЗАЦИИ ===

class Cells(ICells):
    """Класс для управления ячейками игрового поля.
    
    Инвариант: все координаты находятся в пределах rect
    """
    @Contract.on
    def __init__(self, rect: Rect = MAIN_RECT):
        self.check_pre(rect.is_OK, "rect is BAD")
        self._rect = rect
        self.clear()

    @property
    def width(self) -> PositiveInt:
        return self._rect.width

    @property
    def height(self) -> PositiveInt:
        return self._rect.height

    @property
    def rect(self) -> Rect:
        return self._rect

    @Contract.on
    def __getitem__(self, rc: RC) -> Stone:
        self.check_pre(rc.is_OK, "rc is BAD")
        cond = rc in self._rect
        self.check_pre(cond, "Координаты должны быть в пределах поля")
        ans = self._cells[rc.row.value][rc.col.value]
        return ans

    @Contract.on
    def __setitem__(self, rc: RC, stone: Stone) -> None:
        self.check_pre(rc.is_OK, "rc is BAD")
        self.check_pre(rc in self._rect, "Координаты должны быть в пределах поля")
        old_stone = self._cells[rc.row.value][rc.col.value]
        self._cells[rc.row.value][rc.col.value] = stone
        self.check_post(self._cells[rc.row.value][rc.col.value] == stone, "Камень должен быть установлен")
        
    @Contract.on
    def clear(self) -> None:
        self._cells = [[NonStoneValues.EMPTY for _ in range(self.width.value)] for _ in range(self.height.value)]

    @Contract.on
    def erase_rc(self, rc: RC) -> None:
        self.check_pre(rc.is_OK, "rc is BAD")
        self.check_pre(rc in self._rect, "Координаты должны быть в пределах поля")
        self[rc] = NonStoneValues.EMPTY
        self.check_post(self[rc] == NonStoneValues.EMPTY, "Ячейка должна быть пустой")
    
    @Contract.on
    def from_raw(self, stone_strings: list[str]):
        h = self.height.value
        w = self.width.value
        # проверили размеры
        self.check_pre(len(stone_strings) == h, "Неверное количество строк")
        self.check_pre(all(len(stone_strings[i]) == w for i in range(h)), "Неверная длина строк")
        self.check_pre(all(stone_strings[i][j] in StoneFull for i in range(h) for j in range(w)),\
                       "Неверные значения символов в строках")
        for row in range(h):
            for col in range(w):
                self._cells[row][col] = stone_strings[row][col]
    
    def __str__(self) -> str:
        w = self._rect.width.value
        ans = "\n".join([ str(w-i-1)+ " | " + " ".join(map(str, line)) for i, line in enumerate(self._cells[::-1]) ])
        ans += "\n" + "-" * 2 * (w+2)
        ans += "\n  | " + " ".join(map(str, range(w))) + "\n"
        return ans
    
    def __repr__(self) -> str:
        return "Cells\n" + "\n".join(" ".join(map(str, cells_row)) for cells_row in self._cells[::-1])
        

class BonusChest(IBonusChest, Contract):
    """
    Класс для отслеживания бонусов.
    Инвариант: количество всех бонусов >= 0
    """
    def __init__(self):
        super().__init__()
        self.reset()
    
    @Contract.on
    def get_bonus_count(self, bonus: Bonus) -> int:
        result = self._di[bonus]
        self.check_post(result >= 0, "Количество бонусов не может быть отрицательным")
        return result
    
    @Contract.on
    def use_bonus(self, bonus: Bonus) -> None:
        self.check_pre(self._di[bonus] > 0, "Нельзя использовать бонус, которого нет")
        old_count = self._di[bonus]
        self._di[bonus] -= 1
        self.check_post(self._di[bonus] == old_count - 1, "Количество бонусов должно уменьшиться на 1")
        
    @Contract.on
    def add_bonus(self, bonus: Bonus) -> None:
        old_count = self._di[bonus]
        self._di[bonus] += 1
        self.check_post(self._di[bonus] == old_count + 1, "Количество бонусов должно увеличиться на 1")
    
    @Contract.on
    def reset(self) -> None:
        self._di: TypedDict[Bonus, PositiveInt] = {bonus: 0 for bonus in Bonus}
        self.check_post(all(count == 0 for count in self._di.values()), 
                       "Все бонусы должны быть сброшены до нуля")
        
    def __repr__(self) -> str:
        return str(self)
    
    def __str__(self) -> str:
        items = self._di.items()
        ans = ", ".join([str(item[0]) + ": " +str(item[1]) for item in items])
        return "Chest:\n" + ans
    

class Statistics(IStatistics, Contract):
    """
    Класс для отслеживания игровой статистики (очки, бонусы).
    Инвариант: все счетчики >= 0
    Можно наследоваться и добавлять фичи уже более глобальные -- например подсчет ходов
    """
    
    def __init__(self):
        """Инициализация статистики."""
        super().__init__()
        self.reset()
        
    @Contract.on
    def reset(self) -> None:
        """Сброс статистики до начальных значений."""
        self._used_bonus_chest: BonusChest = BonusChest()
        self._scores: PositiveInt = PositiveInt(0)
            
    # === КОМАНДЫ ===
    @Contract.on
    def use_bonus(self, bonus: Bonus) -> None:
        """Регистрирует использование бонуса."""
        self._used_bonus_chest.add_bonus(bonus)


    def increase_scores(self, count: PositiveInt) -> None:
        """Увеличивает количество очков."""
        self._scores = self._scores + count
    
    # === ЗАПРОСЫ ===
    @Contract.on
    def get_scores(self) -> PositiveInt:
        """Возвращает текущее количество очков."""
        return self._scores
    
    @Contract.on
    def get_used_bonus_count(self, bonus: Bonus) -> PositiveInt:
        """Возвращает количество использований указанного бонуса."""
        return self._used_bonus_chest.get_bonus_count(bonus)
    
    @Contract.on
    def __str__(self) -> str:
        """Строковое представление объекта статистики."""
        return f"\nStatistics:\nScores={self._scores}\nUsed bonuses: {self._used_bonus_chest}"

    def __repr__(self) -> str:
        """Строковое представление объекта статистики."""
        return f"\nStatistics:\nScores={self._scores}\nUsed bonuses: {self._used_bonus_chest}"


if __name__ == "__main__":
    rect = Rect(width=PositiveInt(5), height=PositiveInt(6))
    cells = Cells(rect)
    print(cells)