from sqlite3 import Row
from typing import Callable, Tuple

from base import MAIN_RECT, WIDTH, HEIGHT, Stone, NonStoneValues, EraseMaskBonus, Stone, R, C, Bonus, RowInt, ColInt, Rect, PositiveInt, StoneFull, PrinterConstants, Printer
from bounded import T
from cells import Cells, BonusChest, Statistics
from combinations import RC, Mask, COMBINATIONS, ERASE_BONUS_MASKS
from contract import Contract
from random import shuffle
from copy import deepcopy, copy
import random

'''
Реализует запросы и команды "среднего" уровня над Cells
С использованием Масок, без прямого доступа
'''

class Board(Contract):
    """Игровое поле с базовыми операциями над ячейками."""
    @Contract.on
    def __init__(self):
        self._cells = Cells(MAIN_RECT)
        self.check_post(self._cells.is_OK, "cells must be OK")
         
    # ЗАПРОСЫ
    @property
    def height(self) -> int:
        """Высота игрового поля."""
        return self._cells.height

    @property
    def width(self) -> int:
        """Ширина игрового поля."""
        return self._cells.width

    @property
    def rect(self) -> Rect:
        """Прямоугольник игрового поля."""
        return self._cells.rect
    
    def __repr__(self) -> str:
        """Строковое представление объекта игрового поля."""
        return f"\nBoard:\ncells=\n{self._cells}"

    def find_by_value(self, value: Stone) -> Mask:
        """Находит все ячейки с заданным значением."""
        rc_set = [rc for rc in self.rect if self._cells[rc] == value]
        return Mask(rc_set)
    
    def find_equals(self, rc: RC) -> Mask:
        """Находит все ячейки с тем же значением, что и у заданной"""
        value = self._cells[rc]
        return self.find_by_value(value)

    @Contract.on
    def cells_are_equal(self, mask: Mask) -> bool:
        """Проверяет, что все ячейки маски равны друг другу."""
        self.check_pre(not mask.is_empty, "mask must be not empty")
        rc_set = set(mask)
        first_cell = rc_set.pop()
        value = self._cells[first_cell]
        return all([self._cells[rc] == value for rc in rc_set])
    
    def has_empty_cell(self, mask: Mask) -> bool:
        """Проверяет, что в маске есть пустые ячейки."""
        return any([self.is_empty_cell(rc) for rc in set(mask)])
    
    def is_empty_cell(self, rc: RC) -> bool:
        """Проверяет, что ячейка пуста."""
        return self._cells[rc] == NonStoneValues.EMPTY
    
    @property
    def empty_cells(self) -> Mask:
        """Возвращает маску всех пустых ячеек."""
        ans = set(filter(lambda rc: self.is_empty_cell(rc), self.rect))
        return Mask(ans)
    
    @property
    def non_empty_cells(self) -> Mask:
        """Возвращает маску всех непустых ячеек."""
        ans = set(filter(lambda rc: not self.is_empty_cell(rc), self.rect))
        return Mask(ans)

    # КОМАНДЫ
    def _update_rc(self, rc: RC, new_value: Stone) -> None:
        """Обновляет элемент на доске."""
        self._cells[rc] = new_value
    
    def swap(self, rc1: RC, rc2: RC) -> None:
        """Меняет местами два элемента на доске."""
        self._cells[rc2], self._cells[rc1] = self._cells[rc1], self._cells[rc2]
        self.check_post(self._cells.is_OK)
    
    @Printer.on("erase", Printer.PRINT_STEPS_FLAG)
    def erase_mask(self, mask: Mask) -> None:
        """Удаляет элементы с доски по маске."""
        for rc in mask:
            self._cells.erase_rc(rc)

    def update_mask(self, mask: Mask, new_value: Stone) -> None:
        """Обновляет все ячейки маски заданным значением."""
        for rc in mask:
            self._cells[rc] = new_value
    
    def _drop_column(self, col: ColInt) -> None:
        """Сдвигает все элементы вниз в столбце, пустые ячейки поднимаются наверх."""
        h = self.height.value
        new_col = [NonStoneValues.EMPTY] * h
        old_col = [self._cells[RC(RowInt(row), col)] for row in range(h)]
        new_col_index = 0
        for value in old_col:
            if value != NonStoneValues.EMPTY:
                new_col[new_col_index] = value
                new_col_index += 1
        for row in range(h):
            self._update_rc(RC(RowInt(row), col), new_col[row])
    
    @Printer.on("drop", Printer.PRINT_STEPS_FLAG)
    def drop_all(self):
        """Сдвигает все элементы вниз во всех столбцах."""
        for col in range(self.width.value):
            self._drop_column(ColInt(col))   

    @Printer.on("shuffle", Printer.PRINT_STEPS_FLAG)
    def shuffle(self):
        """Перемешивает все элементы на доске."""
        values = [self._cells[rc] for rc in self.rect]
        shuffle(values)
        for i, rc in enumerate(self.rect):
            self._cells[rc] = values[i]
    
    def fill_empty_random(self):
        """Заполняет пустые ячейки случайными элементами."""
        for rc in self.empty_cells:
            self._update_rc(rc, random.choice(list(Stone)))

    @Printer.on("fill line", Printer.PRINT_STEPS_FLAG)
    def fill_first_empty_layer_random(self):
        """Заполняет первую пустую ячейку в каждом столбце случайными элементами."""
        for col in range(self.width.value):
            for row in range(self.height.value):
                if self.is_empty_cell(RC(RowInt(row), ColInt(col))):
                    self._update_rc(RC(RowInt(row), ColInt(col)), random.choice(list(Stone)))
                    break

    def duplicate_rc(self, rc: RC, mask: Mask):
        """Дублирует элемент по всей маске."""
        value = self._cells[rc]
        self._update_mask(mask, value)
        
    def reset(self) -> None:
        """Сбрасывает поле."""
        self._cells.clear()
    
    @Contract.on
    def from_raw(self, stones_strings: list[str]):
        new_cells = Cells(self.rect)
        new_cells.from_raw(stones_strings)
        self.check_pre(new_cells.is_OK, "Ошибка при создании Cells из массива строк")
        self._cells = new_cells
        
    def __str__(self):
        ans = str(self._cells)
        return ans
    
    def __repr__(self):
        return "\n===\nBoard:\n"+str(self)


'''
Фасад над игровым полем, сундуком и статистикой 
'''
class GameBoardSettings:     
    """Настройки игрового поля."""
    BONUS_SCORES = PositiveInt(100)
    SCORES_PER_STONE = PositiveInt(50)
    SWAP_HINT_PREFIX = "Hint: "

# первичные связи между полем, сундуком и статистикой (учет очков)
# атомарные игровые механики

class GameBoard(Contract, GameBoardSettings):
    """Игровое поле с логикой комбинаций и бонусов."""
    
    
    def __init__(self, board: Board, bonus_chest: BonusChest, statistics: Statistics):
        super().__init__()
        self._board = board
        self._chest = bonus_chest
        self._statistics = statistics

    # ЗАПРОСЫ
    @property
    def width(self) -> PositiveInt:
        """Ширина игрового поля."""
        return self._board.width

    @property
    def height(self) -> PositiveInt:
        """Высота игрового поля."""
        return self._board.height

    def has_empty_cells(self) -> bool:
        return len(self._board.empty_cells) > 0

    def get_rc_combination_mask(self, rc: RC) -> Mask:
        """Возвращает маску комбинации для заданной ячейки."""
        # сортируем, чтобы не находил маленькую комбинацию перед большей
        combination_values_sorted = sorted(COMBINATIONS.values(), key=len, reverse=True)
        for combination in combination_values_sorted:
            mask = Mask().from_raw(pivot_raw=rc.raw_repr, mask_raw=combination)
            if len(mask) != len(combination):
                continue
            
            are_equal = self._board.cells_are_equal(mask)
            has_empty = self._board.has_empty_cell(mask)
            if are_equal and not has_empty:
                return mask
        return Mask()

    def is_chest_empty(self) -> bool:
        return all([self._chest.get_bonus_count(bonus) == 0 for bonus in Bonus])
    
    @property
    def has_smart_swap(self) -> bool:
        for rc1 in self._board.non_empty_cells:
            for rc2 in self._board.non_empty_cells:
                if self.is_smart_swap_correct(rc1, rc2):
                    return True
        return False
    
    @Contract.on
    def find_smart_swap(self) -> Tuple[RC, RC]:
        self.check_pre(self.has_smart_swap) 
        for rc1 in self._board.non_empty_cells:
            for rc2 in self._board.non_empty_cells:
                if self.is_smart_swap_correct(rc1, rc2):
                    return (rc1, rc2)
        self.check_post(False, "Ходов обмена нет, но эта функция не должна это проверять!")
        return None, None
    
    def has_combination(self, rc: RC) -> bool:
        """Проверяет наличие комбинации в заданной ячейке."""
        return not self.get_rc_combination_mask(rc).is_empty
    
    def find_combination_mask(self) -> Mask:
        """Находит самую длинную комбинацию на поле."""
        ans = Mask()
        for rc in self._board.non_empty_cells:
            mask = self.get_rc_combination_mask(rc)
            ans = mask if len(ans) < len(mask) else ans
        return ans
    
    def can_use_bonus(self, bonus: Bonus) -> bool:
        """Проверяет возможность использования бонуса."""
        return self._chest.get_bonus_count(bonus) > 0

    def is_swap_correct(self, rc1: RC, rc2: RC) -> bool:
        """Проверяет корректность обмена двух ячеек."""
        is_not_empty1 = not self._board.is_empty_cell(rc1)
        is_not_empty2 = not self._board.is_empty_cell(rc2)
        return is_not_empty1 and is_not_empty2
        
    def is_smart_swap_correct(self, rc1: RC, rc2: RC) -> bool:
        """Проверяет корректность умного обмена двух ячеек."""
        if not self.is_swap_correct(rc1, rc2):
            return False
        if abs(rc1.row.value - rc2.row.value) + abs(rc1.col.value - rc2.col.value) != 1:
            return False
        
        board_copy = deepcopy(self)
        board_copy._board.swap(rc1, rc2)
        mask = board_copy.find_combination_mask()
        return not mask.is_empty
    
    @Contract.on
    def brush_mask(self, rc: RC) -> Mask:
        """Применяет кисть - стирает элементы того же цвета"""
        self.check_pre(not self._board.is_empty_cell(rc), "Нельзя удалять пустую ячейку")
        return self._board.find_equals(rc)
    
    # === КОМАНДЫ ===
    
    def process(self):
        self.drop()
        combination_mask: Mask = self.find_combination_mask()
        while len(combination_mask) > 0 or self.has_empty_cells():
            while len(combination_mask) > 0:
                self.erase_mask(combination_mask)
                self.drop()
                combination_mask = self.find_combination_mask()
            self.fill_line()
            combination_mask = self.find_combination_mask()
                
    @Contract.on
    def use_bonus(self, bonus: Bonus) -> None:
        """Использует бонус и начисляет очки."""
        self.check_pre(self.can_use_bonus(bonus), "Невозможно использовать бонус " + str(bonus))
        self._chest.use_bonus(bonus)
        self._statistics.increase_scores(self.BONUS_SCORES)
        self._statistics.use_bonus(bonus)
    
    def drop(self):
        self._board.drop_all()
    
    def fill_line(self):
        self._board.fill_first_empty_layer_random() 
    
    def erase_mask(self, mask: Mask) -> None:
        """Удаляет маску, начисляет очки, роняет камни и заполняет верхний ряд."""
        self._board.erase_mask(mask)  # стерли
        scores = PositiveInt(self.SCORES_PER_STONE.value * len(mask))  # посчитали очки
        self._statistics.increase_scores(scores)  # увеличили счёт
        
    @Contract.on
    def swap(self, rc1: RC, rc2: RC) -> None:
        """Меняет местами два элемента с проверкой корректности."""
        self.check_pre(self.is_swap_correct(rc1, rc2), "Некорректный обмен")
        self._board.swap(rc1, rc2)
    
    @Contract.on
    def smart_swap(self, rc1: RC, rc2: RC) -> None:
        """Умный обмен двух элементов с проверкой корректности."""
        self.check_pre(self.is_smart_swap_correct(rc1, rc2), "Некорректный умный обмен")
        self._board.swap(rc1, rc2)
            
    def shuffle(self) -> None:
        """Перемешивает все элементы на поле."""
        self._board.shuffle()
    
    def reset(self) -> None:
        """Сбрасывает игру."""
        super()._reset()
        self._board.reset()
        self._chest.reset()
        self._statistics.reset()
        
    def __str__(self):
        board_str = str(self._board)
        chest_str = str(self._chest)
        stat_str = str(self._statistics)
        return "\n".join([board_str, chest_str, stat_str])
    
    def __repr__(self):
        return "\n\n==="+str(self)+"\n\n"
            
  
    
if __name__ == "__main__":
    rc = RC(RowInt(1), ColInt(1))
    # Создаем несколько камней одного цвета
    stones_str_list = ["A"*8, 'B'*8, 'C'*8, 'D'*8, "A"*8, 'B'*8, 'C'*8, 'D'*8]
    board = Board()
    board.from_raw(stones_str_list)
    game_board = GameBoard(board, BonusChest(), Statistics())
    game_board.erase_mask(Mask().from_raw((0,0), ((0, 1), (2,2))))
    print(game_board)
    