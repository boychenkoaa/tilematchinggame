import pytest
import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base import (
    RowInt, ColInt, RowIntExt, ColIntExt, PositiveInt,
    RC, RCExt, Rect, MAIN_RECT, HEIGHT, WIDTH, EraseMaskBonus
)
from combinations import Mask, COMBINATIONS, ERASE_BONUS_MASKS, DEFAULT_PIVOT


# Фикстуры для тестов
@pytest.fixture
def empty_mask():
    return Mask()

@pytest.fixture
def simple_mask():
    rc_set = {
        RC(RowInt(1), ColInt(2)),
        RC(RowInt(2), ColInt(3))
    }
    return Mask(rc_set)

@pytest.fixture
def test_rc_set():
    return {
        RC(RowInt(0), ColInt(0)),
        RC(RowInt(1), ColInt(1)),
        RC(RowInt(2), ColInt(2))
    }


# Тесты для класса Mask
class TestMask:
    def test_init_empty(self):
        # Проверка инициализации пустой маски
        mask = Mask()
        assert mask.is_empty
        assert len(mask) == 0
    
    def test_init_with_rc_set(self, test_rc_set):
        # Проверка инициализации с набором координат
        mask = Mask(test_rc_set)
        assert not mask.is_empty
        assert len(mask) == 3
        
        # Проверяем, что все координаты содержатся в маске
        for rc in test_rc_set:
            assert rc in mask
    
    def test_len(self, empty_mask, simple_mask):
        # Проверка длины пустой маски
        assert len(empty_mask) == 0
        
        # Проверка длины непустой маски
        assert len(simple_mask) == 2
    
    def test_is_empty(self, empty_mask, simple_mask):
        # Проверка пустой маски
        assert empty_mask.is_empty
        
        # Проверка непустой маски
        assert not simple_mask.is_empty
    
    def test_contains(self, simple_mask):
        # Проверка содержания координат в маске
        assert RC(RowInt(1), ColInt(2)) in simple_mask
        assert RC(RowInt(2), ColInt(3)) in simple_mask
        assert RC(RowInt(0), ColInt(0)) not in simple_mask
    
    def test_from_rc_ext_collection(self):
        # Тест создания маски из коллекции RCExt
        mask = Mask()
        pivot = RC(RowInt(2), ColInt(2))
        rc_ext_collection = [
            RCExt(RowIntExt(0), ColIntExt(0)),
            RCExt(RowIntExt(1), ColIntExt(1)),
            RCExt(RowIntExt(-1), ColIntExt(-1))
        ]
        
        result = mask.from_rc_ext_collection(pivot, rc_ext_collection)
        
        # Проверяем, что метод возвращает self
        assert result is mask
        
        # Проверяем содержимое маски
        assert not mask.is_empty
        assert RC(RowInt(2), ColInt(2)) in mask  # pivot + (0,0)
        assert RC(RowInt(3), ColInt(3)) in mask  # pivot + (1,1)
        assert RC(RowInt(1), ColInt(1)) in mask  # pivot + (-1,-1)
    
    def test_mask_iter(self):
        """Тест итерации по маске."""
        # Пустая маска
        empty_mask = Mask()
        assert list(empty_mask) == []
        
        # Маска с элементами
        mask = Mask()
        mask.from_raw((1, 2), ((0, 0), (1, 1), (-1, -1)))
        positions = list(mask)
        assert len(positions) == 3
        assert RC(RowInt(1), ColInt(2)) in positions
        assert RC(RowInt(2), ColInt(3)) in positions
        assert RC(RowInt(0), ColInt(1)) in positions
        
        # Проверка совместимости с for-циклом
        count = 0
        for pos in mask:
            assert pos in mask
            count += 1
        assert count == 3
    
    def test_from_raw(self):
        # Тест создания маски из сырых данных
        mask = Mask()
        pivot_raw = (2, 2)
        mask_raw = ((0, 0), (1, 1), (-1, -1), (10, 10))  # последняя координата выходит за границы
        
        result = mask.from_raw(pivot_raw, mask_raw)
        
        # Проверяем, что метод возвращает self
        assert result is mask
        
        # Проверяем содержимое маски (координаты за границами должны быть отфильтрованы)
        assert not mask.is_empty
        assert len(mask) == 3  # может быть меньше из-за фильтрации
    
    def test_move(self):
        # Тест перемещения маски
        rc_set = {
            RC(RowInt(1), ColInt(1)),
            RC(RowInt(2), ColInt(2))
        }
        mask = Mask(rc_set)
        
        # Перемещаем маску
        delta = RC(RowInt(1), ColInt(1))
        mask.move(delta)
        
        # Проверяем результат
        assert RC(RowInt(2), ColInt(2)) in mask
        assert RC(RowInt(3), ColInt(3)) in mask
        assert RC(RowInt(1), ColInt(1)) not in mask
    
    def test_move_out_of_bounds(self):
        # Тест перемещения маски за границы поля
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


# Интеграционные тесты
class TestMaskIntegration:
    def test_create_mask_from_combination(self):
        # Тест создания маски из предопределенной комбинации
        mask = Mask()
        pivot_raw = (3, 3)
        combo_raw = COMBINATIONS["THREE_1"]
        
        mask.from_raw(pivot_raw, combo_raw)
        
        assert not mask.is_empty()
        assert len(mask) >= 1  # может быть меньше из-за фильтрации границ
    
    def test_create_mask_from_erase_bonus(self):
        # Тест создания маски из бонуса стирания
        mask = Mask()
        pivot_raw = (3, 3)
        bonus_raw = tuple(ERASE_BONUS_MASKS[EraseMaskBonus.ROW])
        mask.from_raw(pivot_raw, bonus_raw)
        
        assert not mask.is_empty()
    
    def test_mask_operations_chain(self):
        # Тест цепочки операций с маской
        mask = Mask()
        
        # Создаем маску из сырых данных
        mask.from_raw((2, 2), ((0, 0), (1, 0), (0, 1)))
        initial_len = len(mask)
        
        # Перемещаем маску
        mask.move(RC(RowInt(1), ColInt(1)))
        
        # Проверяем, что операции выполнились корректно
        assert len(mask) <= initial_len  # может уменьшиться из-за границ


if __name__ == "__main__":
    # Простой тест для проверки работоспособности
    mask = Mask()
    mask.from_raw((0, 0), COMBINATIONS["THREE_1"])
    print(f"Mask length: {len(mask)}")
    print(f"Mask is empty: {mask.is_empty()}")


