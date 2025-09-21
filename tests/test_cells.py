import pytest
from base import Rect, Stone, Stone, NonStoneValues, Bonus, RC, R, C, PositiveInt, RowInt, ColInt
from cells import Cells, BonusChest, Statistics

# Тесты для класса Cells
class TestCells:
    def test_init(self):
        # Проверка инициализации с прямоугольником
        rect = Rect(width=PositiveInt(5), height=PositiveInt(6))
        cells = Cells(rect)
        assert cells.width.value == 5
        assert cells.height.value == 6
        assert cells.rect == rect
        
        # Проверка, что все ячейки инициализированы как EMPTY
        for r in range(cells.height.value):
            for c in range(cells.width.value):
                assert cells[RC(RowInt(r), ColInt(c))] == NonStoneValues.EMPTY
    
    def test_width_height_rect(self):
        rect = Rect(width=PositiveInt(3), height=PositiveInt(4))
        cells = Cells(rect)
        assert cells.width.value == 3
        assert cells.height.value == 4  
        assert cells.rect == rect
    
    def test_getitem(self):
        rect = Rect(width=PositiveInt(3), height=PositiveInt(3))
        cells = Cells(rect)
        # Проверка получения значения ячейки
        assert cells[RC(RowInt(0), ColInt(0))] == NonStoneValues.EMPTY
        assert cells[RC(RowInt(1), ColInt(1))] == NonStoneValues.EMPTY
        assert cells[RC(RowInt(2), ColInt(2))] == NonStoneValues.EMPTY
        
        # Проверка выхода за границы
        cells[RC(RowInt(3), ColInt(3))]
        assert cells.is_ERR
        cells[RC(RowInt(-1), ColInt(0))]
        assert cells.is_ERR
    
    def test_setitem(self):
        rect = Rect(width=PositiveInt(3), height=PositiveInt(3))
        cells = Cells(rect)
        
        # Установка значения ячейки
        cells[RC(RowInt(0), ColInt(0))] = Stone.A
        assert cells[RC(RowInt(0), ColInt(0))] == Stone.A
        
        cells[RC(RowInt(1), ColInt(2))] = Stone.B
        assert cells[RC(RowInt(1), ColInt(2))] == Stone.B
        
        # Проверка выхода за границы
        cells[RC(RowInt(3), ColInt(3))] = Stone.C
        print(cells._status)
        assert cells.is_ERR
        cells[RC(RowInt(-1), ColInt(0))] = Stone.C
        print(cells._status)
        assert cells.is_ERR
    
    def test_clear(self):
        rect = Rect(width=PositiveInt(3), height=PositiveInt(3))
        cells = Cells(rect)
        
        # Заполняем некоторые ячейки
        cells[RC(RowInt(0), ColInt(0))] = Stone.A
        cells[RC(RowInt(1), ColInt(1))] = Stone.B
        cells[RC(RowInt(2), ColInt(2))] = Stone.C
        
        # Очищаем поле
        cells.clear()
        
        # Проверяем, что все ячейки пустые
        for r in range(cells.height.value):
            for c in range(cells.width.value):
                assert cells[RC(RowInt(r), ColInt(c))] == NonStoneValues.EMPTY
    
    def test_erase_rc(self):
        rect = Rect(width=PositiveInt(3), height=PositiveInt(3))
        cells = Cells(rect)
        
        # Заполняем ячейку
        cells[RC(RowInt(1), ColInt(1))] = Stone.A
        assert cells[RC(RowInt(1), ColInt(1))] == Stone.A
        
        # Стираем ячейку
        cells.erase_rc(RC(RowInt(1), ColInt(1)))
        assert cells[RC(RowInt(1), ColInt(1))] == NonStoneValues.EMPTY
        
        # Проверка выхода за границы
        cells.erase_rc(RC(RowInt(3), ColInt(3)))
        assert cells.is_ERR
        cells.erase_rc(RC(RowInt(-1), ColInt(0)))
        assert cells.is_ERR
        cells.erase_rc(RC(RowInt(0), ColInt(-1)))
        assert cells.is_ERR
    
    def test_repr(self):
        """Тест для метода __repr__"""
        rect = Rect(width=PositiveInt(2), height=PositiveInt(2))
        cells = Cells(rect)
        repr_str = repr(cells)
        assert "Cells" in repr_str
        assert isinstance(repr_str, str)
    
    def test_setitem_all_stone_types(self):
        """Тест установки всех типов камней"""
        rect = Rect(width=PositiveInt(3), height=PositiveInt(3))
        cells = Cells(rect)
        
        # Тестируем все типы камней
        stones = [Stone.A, Stone.B, Stone.C, Stone.D, Stone.E, NonStoneValues.EMPTY]
        for i, stone in enumerate(stones):
            if i < 3:  # Используем только доступные позиции
                cells[RC(RowInt(0), ColInt(i))] = stone
                assert cells[RC(RowInt(0), ColInt(i))] == stone
    
    def test_boundary_coordinates(self):
        """Тест граничных координат"""
        rect = Rect(width=PositiveInt(3), height=PositiveInt(3))
        cells = Cells(rect)
        
        # Тестируем граничные валидные координаты
        cells[RC(RowInt(0), ColInt(0))] = Stone.A  # левый верхний угол
        cells[RC(RowInt(2), ColInt(2))] = Stone.B  # правый нижний угол
        cells[RC(RowInt(0), ColInt(2))] = Stone.C  # правый верхний угол
        cells[RC(RowInt(2), ColInt(0))] = Stone.D  # левый нижний угол
        
        assert cells[RC(RowInt(0), ColInt(0))] == Stone.A
        assert cells[RC(RowInt(2), ColInt(2))] == Stone.B
        assert cells[RC(RowInt(0), ColInt(2))] == Stone.C
        assert cells[RC(RowInt(2), ColInt(0))] == Stone.D
        
    def test_from_raw(self):
        """Тест метода from_raw для заполнения поля из строк"""
        rect = Rect(width=PositiveInt(3), height=PositiveInt(2))
        cells = Cells(rect)
        
        # Тестируем корректное заполнение
        stone_strings = [
            "ABC",
            "DE."
        ]
        cells.from_raw(stone_strings)
        
        # Проверяем, что поле заполнено правильно
        assert cells[RC(RowInt(0), ColInt(0))] == Stone.A
        assert cells[RC(RowInt(0), ColInt(1))] == Stone.B
        assert cells[RC(RowInt(0), ColInt(2))] == Stone.C
        assert cells[RC(RowInt(1), ColInt(0))] == Stone.D
        assert cells[RC(RowInt(1), ColInt(1))] == Stone.E
        assert cells[RC(RowInt(1), ColInt(2))] == NonStoneValues.EMPTY
        
        # Тестируем ошибку при неправильном количестве строк
        wrong_height_strings = ["ABC"]
        cells.from_raw(wrong_height_strings)
        assert cells.is_ERR
        
        # Тестируем ошибку при неправильной ширине строки
        wrong_width_strings = [
            "AB",
            "CDE"
        ]
        cells.from_raw(wrong_width_strings)
        assert cells.is_ERR
        
        # Тестируем ошибку при недопустимых символах
        invalid_chars_strings = [
            "ABX",
            "DE."
        ]
        cells.from_raw(invalid_chars_strings)
        assert cells.is_ERR

# Тесты для класса BonusChest
class TestBonusChest:
    def test_init(self):
        chest = BonusChest()
        # Проверяем, что все бонусы инициализированы нулями
        for bonus in Bonus:
            assert chest.get_bonus_count(bonus) == 0
    
    def test_get_bonus_count(self):
        chest = BonusChest()
        # Изначально все бонусы равны 0
        for bonus in Bonus:
            assert chest.get_bonus_count(bonus) == 0
    
    def test_add_bonus(self):
        chest = BonusChest()
        # Добавляем бонусы
        chest.add_bonus(Bonus.BRUSH)
        assert chest.get_bonus_count(Bonus.BRUSH) == 1
        
        chest.add_bonus(Bonus.BRUSH)
        assert chest.get_bonus_count(Bonus.BRUSH) == 2
        
        chest.add_bonus(Bonus.ROW)
        assert chest.get_bonus_count(Bonus.ROW) == 1
        assert chest.get_bonus_count(Bonus.BRUSH) == 2  # Проверяем, что другие бонусы не изменились
    
    def test_use_bonus(self):
        chest = BonusChest()
        # Добавляем бонусы
        chest.add_bonus(Bonus.BRUSH)
        chest.add_bonus(Bonus.BRUSH)
        
        # Используем бонус
        chest.use_bonus(Bonus.BRUSH)
        assert chest.get_bonus_count(Bonus.BRUSH) == 1
        
        chest.use_bonus(Bonus.BRUSH)
        assert chest.get_bonus_count(Bonus.BRUSH) == 0
        
        # Проверка использования бонуса, которого нет
        chest.use_bonus(Bonus.BRUSH)
        assert chest.is_ERR
        assert chest.get_bonus_count(Bonus.BRUSH) == 0
    
    def test_reset(self):
        chest = BonusChest()
        # Добавляем бонусы
        chest.add_bonus(Bonus.BRUSH)
        chest.add_bonus(Bonus.ROW)
        
        # Сбрасываем
        chest.reset()
        
        # Проверяем, что все бонусы сброшены
        for bonus in Bonus:
            assert chest.get_bonus_count(bonus) == 0

# Тесты для класса Statistics
class TestStatistics:
    def test_init(self):
        stats = Statistics()
        # Проверяем начальные значения
        assert stats.get_scores() == PositiveInt(0)
        assert stats.get_moves() == PositiveInt(0)
        assert stats.get_combinations() == PositiveInt(0)
        for bonus in Bonus:
            assert stats.get_used_bonus_count(bonus) == PositiveInt(0)
    
    def test_increase_scores(self):
        stats = Statistics()
        # Увеличиваем очки
        pi = PositiveInt
        stats.increase_scores(pi(10))
        assert stats.get_scores() == PositiveInt(10)
        assert stats.is_OK
        
        stats.increase_scores(pi(5))
        assert stats.get_scores() == 15
        assert stats.is_OK
    
    def test_increase_moves(self):
        stats = Statistics()
        # Увеличиваем ходы
        stats.increase_moves()
        assert stats.get_moves() == 1
        
        stats.increase_moves()
        assert stats.get_moves() == 2
    
    def test_increase_combinations(self):
        stats = Statistics()
        # Увеличиваем комбинации
        stats.increase_combinations()
        assert stats.get_combinations() == 1
        
        stats.increase_combinations()
        assert stats.get_combinations() == 2
    
    def test_use_bonus(self):
        stats = Statistics()
        # Используем бонусы
        stats.use_bonus(Bonus.ROW)
        assert stats.get_used_bonus_count(Bonus.ROW) == 1
        assert stats.get_used_bonus_count(Bonus.BRUSH) == 0
        
        stats.use_bonus(Bonus.COL)
        assert stats.get_used_bonus_count(Bonus.COL) == 1
        assert stats.get_used_bonus_count(Bonus.BRUSH) == 0
        
        stats.use_bonus(Bonus.CROSS)
        assert stats.get_used_bonus_count(Bonus.CROSS) == 1
        assert stats.get_used_bonus_count(Bonus.ROW) == 1  # Проверяем, что другие бонусы не изменились
        assert stats.get_used_bonus_count(Bonus.COL) == 1  # Проверяем, что другие бонусы не изменились
    
    def test_reset(self):
        stats = Statistics()
        # Увеличиваем различные счетчики
        stats.increase_scores(PositiveInt(10))
        stats.increase_moves()
        stats.increase_combinations()
        stats.use_bonus(Bonus.BRUSH)
        
        # Сбрасываем статистику
        stats.reset()
        
        # Проверяем, что все счетчики сброшены
        assert stats.get_scores() == 0
        assert stats.get_moves() == 0
        assert stats.get_combinations() == 0
        for bonus in Bonus:
            assert stats.get_used_bonus_count(bonus) == 0