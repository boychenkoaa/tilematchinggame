import pytest
from unittest.mock import Mock, patch
from copy import deepcopy

from base import PositiveInt, Stone, NonStoneValues, Bonus, RC, RowInt, ColInt, MAIN_RECT
from cells import BonusChest, Statistics
from combinations import Mask
from game_board import Board, GameBoard


class TestBoard:
    """Тесты для класса Board."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.board = Board()
    
    def test_init(self):
        """Тест инициализации доски."""
        assert self.board.width.value > 0
        assert self.board.height.value > 0
        assert self.board.rect == MAIN_RECT
    
    def test_properties(self):
        """Тест свойств доски."""
        assert isinstance(self.board.width, PositiveInt)
        assert isinstance(self.board.height, PositiveInt)
        assert self.board.width.value > 0
        assert self.board.height.value > 0  
    
    def test_find_by_value(self):
        """Тест поиска ячеек по значению."""
        # Заполним несколько ячеек одним значением
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(1), ColInt(1))
        self.board._update_rc(rc1, Stone.A)
        self.board._update_rc(rc2, Stone.A)
        
        mask = self.board.find_by_value(Stone.A)
        assert rc1 in mask
        assert rc2 in mask
        assert len(mask) >= 2
    
    def test_cells_are_equal(self):
        """Тест проверки равенства ячеек в маске."""
        # Создаем маску с одинаковыми значениями
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(0), ColInt(1))
        self.board._update_rc(rc1, Stone.A)
        self.board._update_rc(rc2, Stone.A)
        
        mask = Mask([rc1, rc2])
        assert self.board.cells_are_equal(mask)
        
        # Меняем одно значение
        self.board._update_rc(rc2, Stone.B)
        assert not self.board.cells_are_equal(mask)
    
    def test_has_empty_cell(self):
        """Тест проверки наличия пустых ячеек в маске."""
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(0), ColInt(1))
        
        # Одна ячейка пустая
        self.board._update_rc(rc1, Stone.A)
        mask = Mask([rc1, rc2])
        assert self.board.has_empty_cell(mask)
        
        # Обе ячейки заполнены
        self.board._update_rc(rc2, Stone.B)
        assert not self.board.has_empty_cell(mask)
    
    def test_is_empty_cell(self):
        """Тест проверки пустоты ячейки."""
        rc = RC(RowInt(0), ColInt(0))
        assert self.board.is_empty_cell(rc)
        
        self.board._update_rc(rc, Stone.A)
        assert not self.board.is_empty_cell(rc)
    
    def test_empty_cells_property(self):
        """Тест получения маски пустых ячеек."""
        empty_mask = self.board.empty_cells
        assert len(empty_mask) > 0
        
        # Заполним одну ячейку
        rc = RC(RowInt(0), ColInt(0))
        self.board._update_rc(rc, Stone.A)
        
        new_empty_mask = self.board.empty_cells
        assert len(new_empty_mask) == len(empty_mask) - 1
        assert rc not in new_empty_mask
    
    def test_non_empty_cells_property(self):
        """Тест получения маски непустых ячеек."""
        non_empty_mask = self.board.non_empty_cells
        
        # Заполним одну ячейку
        rc = RC(RowInt(0), ColInt(0))
        self.board._update_rc(rc, Stone.A)
        
        new_non_empty_mask = self.board.non_empty_cells
        assert len(new_non_empty_mask) == len(non_empty_mask) + 1
        assert rc in new_non_empty_mask
    
    def test_swap(self):
        """Тест обмена элементов."""
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(0), ColInt(1))
        
        self.board._update_rc(rc1, Stone.A)
        self.board._update_rc(rc2, Stone.B)
        
        self.board.swap(rc1, rc2)
        
        assert self.board._cells[rc1] == Stone.B
        assert self.board._cells[rc2] == Stone.A
    
    def test_erase_mask(self):
        """Тест удаления элементов по маске."""
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(0), ColInt(1))
        
        self.board._update_rc(rc1, Stone.A)
        self.board._update_rc(rc2, Stone.B)
        
        mask = Mask([rc1, rc2])
        self.board.erase_mask(mask)
        
        assert self.board.is_empty_cell(rc1)
        assert self.board.is_empty_cell(rc2)
    
    def test_update_mask(self):
        """Тест обновления элементов по маске."""
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(0), ColInt(1))
        
        mask = Mask([rc1, rc2])
        self.board.update_mask(mask, Stone.A)
        
        assert self.board._cells[rc1] == Stone.A
        assert self.board._cells[rc2] == Stone.A
    
    def test_drop_column(self):
        """Тест сдвига элементов в столбце."""
        # Заполним столбец с пропуском
        col = ColInt(0)
        self.board._update_rc(RC(RowInt(0), col), Stone.A)
        self.board._update_rc(RC(RowInt(2), col), Stone.B)
        self.board._drop_column(col)
        
        # Элементы должны сдвинуться вниз
        assert self.board._cells[RC(RowInt(0), col)] == Stone.A
        assert self.board._cells[RC(RowInt(1), col)] == Stone.B
    
    def test_drop_all(self):
        """Тест сдвига элементов во всех столбцах."""
        # Заполним доску с пропусками
        for col in range(min(3, self.board.width.value)):
            self.board._update_rc(RC(RowInt(0), ColInt(col)), Stone.A)
            self.board._update_rc(RC(RowInt(2), ColInt(col)), Stone.B)
        
        self.board.drop_all()
        
        # Проверим, что элементы сдвинулись
        for col in range(min(3, self.board.width.value)):
            assert not self.board.is_empty_cell(RC(RowInt(self.board.height - RowInt(1)), ColInt(col)))
            assert not self.board.is_empty_cell(RC(RowInt(self.board.height - RowInt(2)), ColInt(col)))
    
    
    
    def test_fill_empty_random(self):
        """Тест заполнения пустых ячеек случайными элементами."""
        # Частично заполняем доску для более реалистичного теста
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(1), ColInt(1))
        rc3 = RC(RowInt(2), ColInt(2))
        self.board._update_rc(rc1, Stone.A)
        self.board._update_rc(rc2, Stone.B)
        self.board._update_rc(rc3, Stone.C)
        
        empty_count_before = len(self.board.empty_cells)
        assert empty_count_before > 0, "На доске должны быть пустые ячейки для тестирования заполнения"
        
        # Запоминаем заполненные ячейки
        filled_before = {rc: self.board._cells[rc] for rc in [rc1, rc2, rc3]}
        
        self.board.fill_empty_random()
        
        empty_count_after = len(self.board.empty_cells)
        assert empty_count_after == 0
        
        # Проверяем, что ранее заполненные ячейки не изменились
        for rc, expected_value in filled_before.items():
            assert self.board._cells[rc] == expected_value, f"Ячейка {rc} изменилась с {expected_value} на {self.board._cells[rc]}"
    
    def test_reset(self):
        """Тест сброса доски."""
        # Заполняем доску
        rc = RC(RowInt(0), ColInt(0))
        self.board._update_rc(rc, Stone.A)
        
        # Сбрасываем
        self.board.reset()
        
        # Проверяем, что все ячейки пустые
        assert len(self.board.empty_cells) == len(list(self.board.rect))
    
    def test_from_raw(self):
        """заполнение доски списком строк."""
        stone_strings = [
            "ABCDABCD",
            "DCBADCBA",
            "AAAABBBB",
            "CCCCDDDD",
            "EEEEEEEE",
            "AAAAAAAA",
            "BBBBBBBB",
            "BBBBBBBB"
        ]
                
        self.board.from_raw(stone_strings)
        print(self.board.message)
        # Проверяем, что доска заполнена правильно
        assert self.board._cells[RC(RowInt(0), ColInt(0))] == Stone.A
        assert self.board._cells[RC(RowInt(0), ColInt(1))] == Stone.B
        assert self.board._cells[RC(RowInt(1), ColInt(0))] == Stone.D
        assert self.board._cells[RC(RowInt(1), ColInt(1))] == Stone.C
        assert self.board._cells[RC(RowInt(7), ColInt(7))] == "B"
        
        # Тестируем с пустыми ячейками
        stone_strings_with_empty = [
            "ABC.....",
            "DE......",
            "........",
            "........",
            "........",
            "........",
            "........",
            "........"
        ]
        
        self.board.from_raw(stone_strings_with_empty)
        print(self.board.message)
        # Проверяем заполнение с пустыми ячейками
        assert self.board._cells[RC(RowInt(0), ColInt(0))] == Stone.A
        assert self.board._cells[RC(RowInt(0), ColInt(1))] == Stone.B
        assert self.board._cells[RC(RowInt(0), ColInt(2))] == Stone.C
        assert self.board._cells[RC(RowInt(0), ColInt(3))] == NonStoneValues.EMPTY
        assert self.board._cells[RC(RowInt(1), ColInt(0))] == Stone.D
        assert self.board._cells[RC(RowInt(2), ColInt(0))] == NonStoneValues.EMPTY
        
        # Тестируем ошибку при неправильном размере
        wrong_size_strings = ["ABCABCAB", "DCBADCBA", "A", "A", "A", "A", "A", "A"]
        self.board.from_raw(wrong_size_strings)
        assert self.board.is_ERR
        
        wrong_size_strings = ["ABCABCAB", "DCBADCBA", "ABCABCAB", 
                              "DCBADCBA", "ABCABCAB", "DCBADCBA",
                              "ABCABCAB", "DCBADCBA", "DCBADCBA"]
        self.board.from_raw(wrong_size_strings)
        assert self.board.is_ERR
        
        wrong_size_strings = ["ABCABCAB", "DCBADCBA", "ABCABCAB", 
                              "DCBADCBA", "ABCABCAB", "DCBADCB",
                              "ABCABCAB", "DCBADCBA"]
        self.board.from_raw(wrong_size_strings)
        assert self.board.is_ERR
        
        # неправильыне буквы
        wrong_letters_strings = ["ABCAZCAB", "DCBADCBA", "ABCABCAB", 
                              "ADXXXCBA", "ABCABCAB", "DCBADCBA",
                              "ABCABCAB", "DCBADCBA"]
        self.board.from_raw(wrong_letters_strings)
        assert self.board.is_ERR



class TestGameBoard:
    """Тесты для класса GameBoard."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.board = Board()
        self.bonus_chest = Mock(spec=BonusChest)
        self.statistics = Mock(spec=Statistics)
        self.game_board = GameBoard(self.board, self.bonus_chest, self.statistics)
    
    def test_init(self):
        """Тест инициализации игрового поля."""
        assert self.game_board.width == self.board.width
        assert self.game_board.height == self.board.height
    
    def test_properties(self):
        """Тест свойств игрового поля."""
        assert self.game_board.width.value > 0
        assert self.game_board.height.value > 0
    
    def test_get_rc_combination_mask_no_combination(self):
        """Тест получения маски комбинации - нет комбинации."""
        rc = RC(RowInt(0), ColInt(0))
        self.board._update_rc(rc, Stone.A)
        
        mask = self.game_board.get_rc_combination_mask(rc)
        assert mask.is_empty
    
    def test_has_combination(self):
        """Тест проверки наличия комбинации."""
        rc = RC(RowInt(0), ColInt(0))
        self.board._update_rc(rc, Stone.A)
        
        # Без комбинации
        assert not self.game_board.has_combination(rc)
    
    def test_find_combination_mask_empty(self):
        """Тест поиска комбинации - пустой результат."""
        # Заполним доску без комбинаций
        pattern = [Stone.A, Stone.B, Stone.C, Stone.D]
        for i, rc in enumerate(list(self.board.rect)[:10]):
            self.board._update_rc(rc, pattern[i % 4])
        
        mask = self.game_board.find_combination_mask()
        assert mask.is_empty
    
    def test_find_combination_mask_three_horizontal(self):
        """Тест поиска горизонтальной комбинации из трех."""
        # Создаем горизонтальную комбинацию THREE_1: ((0, 0), (-1, 0), (1, 0))
        center_rc = RC(RowInt(2), ColInt(2))
        left_rc = RC(RowInt(1), ColInt(2))  # (-1, 0) от центра
        right_rc = RC(RowInt(3), ColInt(2))  # (1, 0) от центра
        
        # Заполняем одинаковыми камнями
        self.board._update_rc(center_rc, Stone.A)
        self.board._update_rc(left_rc, Stone.A)
        self.board._update_rc(right_rc, Stone.A)
        
        mask = self.game_board.find_combination_mask()
        assert not mask.is_empty
        assert len(mask) == 3
        assert center_rc in mask
        assert left_rc in mask
        assert right_rc in mask
    
    def test_find_combination_mask_three_vertical(self):
        """Тест поиска вертикальной комбинации из трех."""
        # Создаем вертикальную комбинацию THREE_2: ((0, 0), (0, -1), (0, 1))
        center_rc = RC(RowInt(2), ColInt(2))
        up_rc = RC(RowInt(2), ColInt(1))    # (0, -1) от центра
        down_rc = RC(RowInt(2), ColInt(3))  # (0, 1) от центра
        
        # Заполняем одинаковыми камнями
        self.board._update_rc(center_rc, Stone.B)
        self.board._update_rc(up_rc, Stone.B)
        self.board._update_rc(down_rc, Stone.B)
        
        mask = self.game_board.find_combination_mask()
        assert not mask.is_empty
        assert len(mask) == 3
        assert center_rc in mask
        assert up_rc in mask
        assert down_rc in mask
    
    def test_find_combination_mask_four_horizontal(self):
        """Тест поиска горизонтальной комбинации из четырех."""
        # Создаем комбинацию FOUR_1: ((-1, 0), (0, 0), (1, 0), (2, 0))
        rc1 = RC(RowInt(1), ColInt(2))  # (-1, 0)
        rc2 = RC(RowInt(2), ColInt(2))  # (0, 0) - центр
        rc3 = RC(RowInt(3), ColInt(2))  # (1, 0)
        rc4 = RC(RowInt(4), ColInt(2))  # (2, 0)
        
        # Заполняем одинаковыми камнями
        for rc in [rc1, rc2, rc3, rc4]:
            self.board._update_rc(rc, Stone.C)
        
        mask = self.game_board.find_combination_mask()
        assert not mask.is_empty
        assert len(mask) == 4
        for rc in [rc1, rc2, rc3, rc4]:
            assert rc in mask
    
    def test_find_combination_mask_l_shape(self):
        """Тест поиска L-образной комбинации."""
        # Создаем комбинацию L1: ((0, 2), (0, 1), (0, 0), (1, 0), (2, 0))
        center_rc = RC(RowInt(2), ColInt(2))  # (0, 0)
        rc1 = RC(RowInt(2), ColInt(4))        # (0, 2)
        rc2 = RC(RowInt(2), ColInt(3))        # (0, 1)
        rc3 = RC(RowInt(3), ColInt(2))        # (1, 0)
        rc4 = RC(RowInt(4), ColInt(2))        # (2, 0)
        
        # Заполняем одинаковыми камнями
        for rc in [center_rc, rc1, rc2, rc3, rc4]:
            self.board._update_rc(rc, Stone.D)
        
        mask = self.game_board.find_combination_mask()
        assert not mask.is_empty
        assert len(mask) == 5
        for rc in [center_rc, rc1, rc2, rc3, rc4]:
            assert rc in mask
    
    def test_find_combination_mask_t_shape(self):
        """Тест поиска T-образной комбинации."""
        # Создаем комбинацию T1: ((-2, 0), (-1, 0), (0,0), (1, 0), (2,0), (0,1), (0,2))
        center_rc = RC(RowInt(3), ColInt(3))  # (0, 0)
        # Горизонтальная линия
        rc1 = RC(RowInt(1), ColInt(3))        # (-2, 0)
        rc2 = RC(RowInt(2), ColInt(3))        # (-1, 0)
        rc3 = RC(RowInt(4), ColInt(3))        # (1, 0)
        rc4 = RC(RowInt(5), ColInt(3))        # (2, 0)
        # Вертикальная часть
        rc5 = RC(RowInt(3), ColInt(4))        # (0, 1)
        rc6 = RC(RowInt(3), ColInt(5))        # (0, 2)
        
        # Заполняем одинаковыми камнями
        for rc in [center_rc, rc1, rc2, rc3, rc4, rc5, rc6]:
            self.board._update_rc(rc, Stone.E)
        
        mask = self.game_board.find_combination_mask()
        assert not mask.is_empty
        assert len(mask) == 7
        for rc in [center_rc, rc1, rc2, rc3, rc4, rc5, rc6]:
            assert rc in mask
    
    def test_find_combination_mask_with_empty_cells(self):
        """Тест что комбинация не находится при наличии пустых ячеек."""
        # Создаем почти комбинацию, но с пустой ячейкой
        center_rc = RC(RowInt(2), ColInt(2))
        left_rc = RC(RowInt(1), ColInt(2))
        right_rc = RC(RowInt(3), ColInt(2))
        
        # Заполняем только две из трех ячеек
        self.board._update_rc(center_rc, Stone.A)
        self.board._update_rc(left_rc, Stone.A)
        # right_rc остается пустой
        
        mask = self.game_board.find_combination_mask()
        assert mask.is_empty
    
    def test_find_combination_mask_different_stones(self):
        """Тест что комбинация не находится при разных типах камней."""
        # Создаем расположение как для комбинации, но с разными камнями
        center_rc = RC(RowInt(2), ColInt(2))
        left_rc = RC(RowInt(1), ColInt(2))
        right_rc = RC(RowInt(3), ColInt(2))
        
        # Заполняем разными камнями
        self.board._update_rc(center_rc, Stone.A)
        self.board._update_rc(left_rc, Stone.B)
        self.board._update_rc(right_rc, Stone.C)
        
        mask = self.game_board.find_combination_mask()
        assert mask.is_empty
    

    def test_is_swap_correct(self):
        """Тест проверки корректности обмена."""
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(0), ColInt(1))
        
        # Пустые ячейки - некорректный обмен
        assert not self.game_board.is_swap_correct(rc1, rc2)
        
        # Заполненные ячейки - корректный обмен
        self.board._update_rc(rc1, Stone.A)
        self.board._update_rc(rc2, Stone.B)
        assert self.game_board.is_swap_correct(rc1, rc2)
    
    def test_use_bonus_comprehensive(self):
        abcd_board  = Board()
        abcd_board.from_raw(["ABCDABCD"]*8)
        game_board = GameBoard(abcd_board, BonusChest(), Statistics())
        
        assert not game_board.can_use_bonus(Bonus.CROSS)
        assert not game_board.can_use_bonus(Bonus.ROW)
            
        # Добавляем два разных бонуса в сундук
        game_board._chest.add_bonus(Bonus.CROSS)
        game_board._chest.add_bonus(Bonus.ROW)
        
        # Проверяем, что теперь можем использовать эти бонусы
        assert game_board.can_use_bonus(Bonus.CROSS)
        assert game_board.can_use_bonus(Bonus.ROW)
            
        # Используем первый бонус
        initial_scores = game_board._statistics.get_scores()
        game_board.use_bonus(Bonus.CROSS)
        assert game_board.is_OK
        assert game_board._statistics.get_scores() == initial_scores + game_board.BONUS_SCORES
        assert not game_board.can_use_bonus(Bonus.CROSS)  # Бонус использован
        assert game_board.can_use_bonus(Bonus.ROW)  # Второй бонус остался
            
        # Используем второй бонус
        current_scores = game_board._statistics.get_scores()
        game_board.use_bonus(Bonus.ROW)
        assert game_board.is_OK
        assert game_board._statistics.get_scores() == current_scores + game_board.BONUS_SCORES
        assert not game_board.can_use_bonus(Bonus.ROW)  # Второй бонус использован
            
        # Теперь сундук пуст, пытаемся использовать бонус
        game_board.use_bonus(Bonus.CROSS)
        assert game_board.is_ERR  # Ошибка - бонуса нет в сундуке
            
        # Проверяем, что состояние сохранилось (очки не изменились)
        assert game_board._statistics.get_scores() == current_scores + game_board.BONUS_SCORES
    
    def test_erase_mask(self):
        """Тест удаления маски с начислением очков."""
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(0), ColInt(1))
        
        self.board._update_rc(rc1, Stone.A)
        self.board._update_rc(rc2, Stone.B)
        
        mask = Mask([rc1, rc2])
        
        with patch.object(self.board, 'drop_all') as mock_drop, \
             patch.object(self.board, 'fill_first_empty_layer_random') as mock_fill:
            
            self.game_board.erase_mask(mask)
            
            # Проверим, что ячейки стерты
            assert self.board.is_empty_cell(rc1)
            assert self.board.is_empty_cell(rc2)
            
            # Проверим начисление очков
            expected_scores = 50 * 2  # SCORES_PER_STONE * количество камней
            self.statistics.increase_scores.assert_called_once_with(expected_scores)
            
            # Проверим вызов дополнительных методов
            mock_drop.assert_called_once()
            mock_fill.assert_called_once()
    
    def test_swap_success(self):
        """Тест успешного обмена камней."""
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(0), ColInt(1))
        
        self.board._update_rc(rc1, Stone.A)
        self.board._update_rc(rc2, Stone.B)
        
        original_stone1 = self.board._cells[rc1]
        original_stone2 = self.board._cells[rc2]
        
        self.game_board.swap(rc1, rc2)
        
        assert self.game_board.is_OK
        assert self.board._cells[rc1] == original_stone2
        assert self.board._cells[rc2] == original_stone1

    def test_swap_precondition_violation(self):
        """Тест нарушения предусловий при обмене камней."""
        rc1 = RC(RowInt(0), ColInt(0))
        rc2 = RC(RowInt(2), ColInt(2))  # пустая клетка
        
        self.board._update_rc(rc1, Stone.A)
        # self.board._update_rc(rc2, Stone.B)
        
        original_stone1 = self.board._cells[rc1]
        original_stone2 = self.board._cells[rc2]
        
        self.game_board.swap(rc1, rc2)
        
        assert self.game_board.is_ERR
        # Проверяем, что состояние доски не изменилось
        assert self.board._cells[rc1] == original_stone1
        assert self.board._cells[rc2] == original_stone2

    def test_smart_swap_comprehensive(self):
        abcd_board  = Board()
        abcd_board.from_raw([
            "ABCDABCD",
            "DBCAABCD",
            "BDABABCD",
            "BCADABCD"]*2)
        game_board = GameBoard(abcd_board, BonusChest(), Statistics())
        
        # Координаты для успешного обмена
        rc_success1 = RC(RowInt(0), ColInt(1))  # Stone.A
        rc_success2 = RC(RowInt(1), ColInt(1))  # Stone.B
            
        # 1. Сначала тестируем неудачный обмен (не соседние клетки)
        rc_fail1 = RC(RowInt(1), ColInt(0))
        rc_fail2 = RC(RowInt(2), ColInt(2))
        
        original_stone_fail1 = game_board._board._cells[rc_fail1]
        original_stone_fail2 = game_board._board._cells[rc_fail2]
            
        # Попытка неудачного обмена
        assert not  game_board.is_smart_swap_correct(rc_fail1, rc_fail2)
        game_board.smart_swap(rc_fail1, rc_fail2)
            
        # 2. Проверяем статус ошибки
        assert game_board.is_ERR
        # Проверяем, что состояние доски не изменилось
        assert game_board._board._cells[rc_fail1] == original_stone_fail1
        assert game_board._board._cells[rc_fail2] == original_stone_fail2
            
        # Сброс состояния ошибки
        abcd_board.from_raw(["ABABABAB","BABABABA"]*4)
        game_board = GameBoard(abcd_board, BonusChest(), Statistics())
            
        # 3. Проверяем, что изначально нет комбинации
        assert game_board.find_combination_mask().is_empty
            
        # 4. Делаем успешный обмен
        game_board.smart_swap(rc_success1, rc_success2)
            
        # 5. Проверяем статус ОК
        assert game_board.is_OK
            
        # 6. Проверяем, что камни поменялись местами
        assert game_board._board._cells[rc_success1] == Stone.A  # Теперь здесь Stone.B
        assert game_board._board._cells[rc_success2] == Stone.B  # Теперь здесь Stone.A
            
        # 7. Проверяем, что появилась комбинация
        # После обмена получается: AAABABAB, BBBABABA
        assert game_board.has_combination(rc_success1)
        assert game_board.has_combination(rc_success2)
            
        # 8. Дополнительная проверка: получаем маску комбинации
        mask = game_board.find_combination_mask()
        assert len(mask) > 0
        # Проверяем, что позиции с камнями A входят в комбинацию
        expected_positions = {
            RC(RowInt(0), ColInt(0)),  # A (после обмена)
            RC(RowInt(0), ColInt(1)),  # A
            RC(RowInt(0), ColInt(2))   # A
        }
        assert expected_positions == set(mask)

    def test_get_rc_combination_mask_with_combination(self):
        """Тест получения маски комбинации для конкретной клетки."""
        # Создаем горизонтальную комбинацию
        for col in range(3):
            self.board._update_rc(RC(RowInt(0), ColInt(col)), Stone.A)
        
        rc = RC(RowInt(0), ColInt(1))
        mask = self.game_board.get_rc_combination_mask(rc)
        
        assert len(mask) > 0
        assert rc in mask

    def test_has_combination_true(self):
        """Тест проверки наличия комбинаций - положительный случай."""
        # Создаем вертикальную комбинацию
        for row in range(3):
            self.board._update_rc(RC(RowInt(row), ColInt(0)), Stone.B)
        
        assert self.game_board.has_combination(RC(RowInt(1), ColInt(0)))

    def test_has_combination_false(self):
        """Тест проверки наличия комбинаций - отрицательный случай."""
        # Заполняем доску без комбинаций
        self.board._update_rc(RC(RowInt(0), ColInt(0)), Stone.A)
        self.board._update_rc(RC(RowInt(0), ColInt(1)), Stone.B)
        self.board._update_rc(RC(RowInt(1), ColInt(0)), Stone.C)
        
        assert not self.game_board.has_combination(RC(RowInt(1), ColInt(0)))

    def test_brushmask(self):
        """Тест применения кисти."""
        rc = RC(RowInt(1), ColInt(1))
        # Создаем несколько камней одного цвета
        stones_str_list = ["A"*8, 'B'*8, 'C'*8, 'D'*8, "A"*8, 'B'*8, 'C'*8, 'D'*8]
        self.board.from_raw(stones_str_list)
        mask = self.game_board.brush_mask(rc)
        assert len(mask) == 16
    
    def test_shuffle(self):
        """Тест перемешивания игрового поля."""
        # Заполняем доску известными значениями для тестирования
        test_values = [Stone.A, Stone.B, Stone.C, Stone.D, Stone.E]
        for i, rc in enumerate(self.board.rect):
            stone = test_values[i % len(test_values)]
            self.board._update_rc(rc, stone)
        
        # Подсчитываем количество каждого типа тайлов до перемешивания
        count_before = {}
        for rc in self.board.rect:
            tile_value = self.board._cells[rc]
            count_before[tile_value] = count_before.get(tile_value, 0) + 1
        
        # Выполняем перемешивание
        self.board.shuffle()
        
        # Подсчитываем количество каждого типа тайлов после перемешивания
        count_after = {}
        for rc in self.board.rect:
            tile_value = self.board._cells[rc]
            count_after[tile_value] = count_after.get(tile_value, 0) + 1
        
        # Проверяем, что количество тайлов каждого типа не изменилось
        assert count_before == count_after, f"Количество тайлов изменилось: до={count_before}, после={count_after}"
        
        # Дополнительная проверка: общее количество тайлов должно остаться тем же
        total_before = sum(count_before.values())
        total_after = sum(count_after.values())
        assert total_before == total_after, f"Общее количество тайлов изменилось: {total_before} -> {total_after}"