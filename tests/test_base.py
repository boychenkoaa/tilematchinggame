import pytest
import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base import (
    RowInt, ColInt, RowIntExt, ColIntExt, PositiveInt,
    Stone, Stone, NonStoneValues, EraseMaskBonus, ActionBonus, Bonus,
    RC, Rect, MAIN_RECT, WIDTH, HEIGHT
)


# Тесты для ограниченных типов целых чисел
class TestBoundedTypes:
    def test_row_int_valid(self):
        # Проверка создания допустимых значений RowInt
        row = RowInt(0)
        assert row.value == 0
        row = RowInt(HEIGHT - 1)
        assert row.value == HEIGHT - 1
    
    def test_row_int_invalid(self):
        # Проверка исключений при недопустимых значениях
        a = RowInt(-1)
        assert a.is_ERR
        b = RowInt(HEIGHT)
        assert b.is_ERR
    
    def test_col_int_valid(self):
        # Проверка создания допустимых значений ColInt
        col = ColInt(0)
        assert col.value == 0
        col = ColInt(WIDTH - 1)
        assert col.value == WIDTH - 1
    
    def test_col_int_invalid(self):
        # Проверка исключений при недопустимых значениях
        a = ColInt(-1)
        assert a.is_ERR
        b = ColInt(WIDTH)
        assert b.is_ERR
    
    def test_row_int_ext_valid(self):
        # Проверка создания допустимых значений RowIntExt
        row = RowIntExt(-HEIGHT)
        assert row.value == -HEIGHT
        row = RowIntExt(HEIGHT)
        assert row.value == HEIGHT
    
    def test_col_int_ext_valid(self):
        # Проверка создания допустимых значений ColIntExt
        col = ColIntExt(-WIDTH)
        assert col.value == -WIDTH
        col = ColIntExt(WIDTH)
        assert col.value == WIDTH
    
    def test_positive_int_valid(self):
        # Проверка создания допустимых значений PositiveInt
        pos = PositiveInt(0)
        assert pos.value == 0
        pos = PositiveInt(100)
        assert pos.value == 100
    
    def test_positive_int_invalid(self):
        # Проверка исключений при недопустимых значениях
        a = PositiveInt(-1)
        assert a.is_ERR


# Тесты для перечислений
class TestStoneEnums:
    def test_stone_values(self):
        # Проверка значений перечисления Stone
        assert Stone.A == "A"
        assert Stone.B == "B"
        assert Stone.C == "C"
        assert Stone.D == "D"
    
    def test_stone_full_values(self):
        # Проверка значений перечисления StoneFull
        assert Stone.A == "A"
        assert Stone.B == "B"
        assert Stone.C == "C"
        assert Stone.D == "D"
        assert NonStoneValues.EMPTY == "."
    
    def test_erase_mask_bonus_values(self):
        # Проверка значений перечисления EraseMaskBonus
        assert EraseMaskBonus.ALL == "ALL"
        assert EraseMaskBonus.COL == "COL"
        assert EraseMaskBonus.ROW == "ROW"
        assert EraseMaskBonus.CROSS == "CROSS"
    
    def test_action_bonus_values(self):
        # Проверка значений перечисления ActionBonus
        assert ActionBonus.BRUSH == "BRUSH"
        assert ActionBonus.SHUFFLE == "SHUFFLE"
        assert ActionBonus.SWAP == "SWAP"
    
    def test_bonus_inheritance(self):
        # Проверка наследования в перечислении Bonus
        assert Bonus.ALL == "ALL"
        assert Bonus.COL == "COL"
        assert Bonus.ROW == "ROW"
        assert Bonus.CROSS == "CROSS"
        assert Bonus.BRUSH == "BRUSH"
        assert Bonus.SHUFFLE == "SHUFFLE"
        assert Bonus.SWAP == "SWAP"


# Тесты для класса RC
class TestRC:
    def test_rc_creation(self):
        # Проверка создания объекта RC
        rc = RC(RowInt(1), ColInt(2))
        assert rc.row.value == 1
        assert rc.col.value == 2
    
    def test_rc_addition(self):
        # Проверка операции сложения
        rc1 = RC(RowInt(1), ColInt(2))
        rc2 = RC(RowInt(3), ColInt(4))
        result = rc1 + rc2
        assert result.row.value == 4
        assert result.col.value == 6
    
    def test_rc_subtraction(self):
        # Проверка операции вычитания
        rc1 = RC(RowInt(5), ColInt(7))
        rc2 = RC(RowInt(2), ColInt(3))
        result = rc1 - rc2
        assert result.row.value == 3
        assert result.col.value == 4
    
    def test_rc_equality(self):
        # Проверка операции сравнения
        rc1 = RC(RowInt(1), ColInt(2))
        rc2 = RC(RowInt(1), ColInt(2))
        rc3 = RC(RowInt(3), ColInt(4))
        assert rc1 == rc2
        assert rc1 != rc3


# Тесты для класса Rect
class TestRect:
    def test_rect_creation(self):
        # Проверка создания объекта Rect
        rect = Rect(PositiveInt(WIDTH), PositiveInt(HEIGHT))
        assert rect.width.value == WIDTH
        assert rect.height.value == HEIGHT
    
    def test_rect_contains(self):
        # Проверка метода __contains__
        rect = Rect(PositiveInt(WIDTH), PositiveInt(HEIGHT))
        rc_inside = RC(RowInt(0), ColInt(0))
        assert rc_inside in rect
        
        rc_inside2 = RC(RowInt(HEIGHT-1), ColInt(WIDTH-1))
        assert rc_inside2 in rect
    
    def test_rect_iteration(self):
        # Проверка итерации по прямоугольнику
        rect = Rect(PositiveInt(2), PositiveInt(2))
        points = list(rect)
        assert len(points) == 4
        assert points[0].row.value == 0
        assert points[0].col.value == 0
        assert points[1].row.value == 0
        assert points[1].col.value == 1
        assert points[2].row.value == 1
        assert points[2].col.value == 0
        assert points[3].row.value == 1
        assert points[3].col.value == 1


# Тесты для константы MAIN_RECT
def test_main_rect_dimensions():
    # Проверка размеров основного прямоугольника
    assert MAIN_RECT.height.value == HEIGHT
    assert MAIN_RECT.width.value == WIDTH


# Использование фикстур pytest для повторяющихся объектов
@pytest.fixture
def sample_rc():
    return RC(RowInt(1), ColInt(2))

@pytest.fixture
def sample_rect():
    return Rect(PositiveInt(WIDTH), PositiveInt(HEIGHT))


# Пример использования фикстур
def test_rc_with_fixture(sample_rc):
    assert sample_rc.row.value == 1
    assert sample_rc.col.value == 2

def test_rect_with_fixture(sample_rect):
    assert sample_rect.width.value == WIDTH
    assert sample_rect.height.value == HEIGHT