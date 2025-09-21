import pytest
import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bounded import BoundedInt
from contract import ContractErrPreException

@pytest.fixture
def simple_bounded_type():
    return BoundedInt.create_bounded_type(0, 10, "TestBoundedInt")

@pytest.fixture
def negative_bounded_type():
    return BoundedInt.create_bounded_type(-5, 5, "NegativeBoundedInt")


class TestBoundedIntCreation:
    def test_create_valid_instance(self, simple_bounded_type):
        # Проверка создания экземпляра с допустимым значением
        bounded_int = simple_bounded_type(5)
        assert bounded_int.value == 5
        assert str(bounded_int) == "5"
        assert repr(bounded_int) == "TestBoundedInt(5)"
        assert int(bounded_int) == 5
    
    def test_create_min_value(self, simple_bounded_type):
        # Проверка создания экземпляра с минимальным значением
        bounded_int = simple_bounded_type(0)
        assert bounded_int.value == 0
    
    def test_create_max_value(self, simple_bounded_type):
        # Проверка создания экземпляра с максимальным значением
        bounded_int = simple_bounded_type(10)
        assert bounded_int.value == 10
     
    def test_create_invalid_below_min(self, simple_bounded_type):
        # Проверка исключения при создании с значением ниже минимального
        a = simple_bounded_type(-1)
        assert not a.is_OK
    
    def test_create_invalid_above_max(self, simple_bounded_type):
        # Проверка исключения при создании с значением выше максимального
        assert not simple_bounded_type(11).is_OK
    
    def test_create_invalid_non_int(self, simple_bounded_type):
        # Проверка исключения при создании с нецелочисленным значением
        assert not simple_bounded_type("not an int").is_OK
        assert not simple_bounded_type(5.5).is_OK


class TestBoundedIntOperations:
    def test_value_property(self, simple_bounded_type):
        # Проверка свойства value
        bounded_int = simple_bounded_type(5)
        assert bounded_int.value == 5
        
        # Изменение значения через свойство
        bounded_int.value = 7
        assert bounded_int.is_OK
        assert bounded_int.value == 7
    
    def test_value_property_invalid(self, simple_bounded_type):
        # Проверка исключения при установке недопустимого значения
        bounded_int = simple_bounded_type(5)
        bounded_int.value = -1
        assert bounded_int.is_ERR
        bounded_int.value = 11
        assert bounded_int.is_ERR
    
    def test_equality(self, simple_bounded_type):
        # Проверка оператора равенства
        bounded_int1 = simple_bounded_type(5)
        bounded_int2 = simple_bounded_type(5)
        bounded_int3 = simple_bounded_type(7)
        
        assert bounded_int1 == bounded_int2
        assert bounded_int1 != bounded_int3
        assert bounded_int1 == 5  # Сравнение с обычным int
        assert bounded_int1 != 7
    
    def test_addition(self, simple_bounded_type):
        # Проверка оператора сложения
        bounded_int1 = simple_bounded_type(3)
        bounded_int2 = simple_bounded_type(4)
        result = bounded_int1 + bounded_int2
        
        assert isinstance(result, simple_bounded_type)
        assert result.value == 7
    
    def test_addition_overflow(self, simple_bounded_type):
        # Проверка исключения при переполнении при сложении
        bounded_int1 = simple_bounded_type(7)
        bounded_int2 = simple_bounded_type(5)
        result = bounded_int1 + bounded_int2  # 7 + 5 = 12, что больше max_value=10
        assert result.is_ERR
    
    def test_subtraction(self, simple_bounded_type):
        # Проверка оператора вычитания
        bounded_int1 = simple_bounded_type(7)
        bounded_int2 = simple_bounded_type(4)
        result = bounded_int1 - bounded_int2
        
        assert isinstance(result, simple_bounded_type)
        assert result.value == 3
    
    def test_subtraction_underflow(self, simple_bounded_type):
        # Проверка исключения при выходе за нижнюю границу при вычитании
        bounded_int1 = simple_bounded_type(3)
        bounded_int2 = simple_bounded_type(5)
        
        result = bounded_int1 - bounded_int2  # 3 - 5 = -2, что меньше min_value=0
        assert result.is_ERR
    
    def test_multiplication(self, simple_bounded_type):
        # Проверка оператора умножения
        bounded_int1 = simple_bounded_type(2)
        bounded_int2 = simple_bounded_type(3)
        result = bounded_int1 * bounded_int2
        
        assert isinstance(result, simple_bounded_type)
        assert result.value == 6
    
    def test_multiplication_overflow(self, simple_bounded_type):
        # Проверка исключения при переполнении при умножении
        bounded_int1 = simple_bounded_type(5)
        bounded_int2 = simple_bounded_type(3)
        
        result = bounded_int1 * bounded_int2  # 5 * 3 = 15, что больше max_value=10
        assert result.is_ERR


class TestBoundedIntFactory:
    def test_create_bounded_type(self):
        # Проверка создания нового типа
        TestType = BoundedInt.create_bounded_type(0, 100, "TestType")
        assert TestType.min_value == 0
        assert TestType.max_value == 100
        
        # Создание экземпляра нового типа
        test_instance = TestType(50)
        assert test_instance.value == 50
    
    def test_create_bounded_type_default_name(self):
        # Проверка создания типа с автоматическим именем
        TestType = BoundedInt.create_bounded_type(0, 100)
        assert TestType.__name__ == "BoundedInt_0_100"
    
    def test_create_bounded_type_invalid_range(self):
        # Проверка исключения при создании типа с недопустимым диапазоном
        with pytest.raises(ValueError):
            test_type = BoundedInt.create_bounded_type(10, 5)  # min > max
            assert(test_type.is_ERR)
    
    def test_negative_range(self):
        # Проверка создания типа с отрицательными значениями
        NegativeType = BoundedInt.create_bounded_type(-10, -1, "NegativeType")
        assert NegativeType.min_value == -10
        assert NegativeType.max_value == -1
        
        # Создание экземпляра с отрицательным значением
        neg_instance = NegativeType(-5)
        assert neg_instance.value == -5
        
        # Проверка исключения при выходе за границы
        neg_instance = NegativeType(0)
        assert neg_instance.is_ERR


def test_different_bounded_types():
    # Проверка независимости разных типов
    TypeA = BoundedInt.create_bounded_type(0, 10, "TypeA")
    TypeB = BoundedInt.create_bounded_type(100, 200, "TypeB")
    
    instance_a = TypeA(5)
    instance_b = TypeB(150)
    
    assert instance_a.value == 5
    assert instance_b.value == 150
    
    # Проверка, что границы разных типов не влияют друг на друга
    a = TypeA(150)  # Допустимо для TypeB, но не для TypeA
    assert a.is_ERR
    
    b = TypeB(5)  # Допустимо для TypeA, но не для TypeB
    assert b.is_ERR

if __name__ == "__main__":
    simple_bounded_type = BoundedInt.create_bounded_type(0, 10, "TestBoundedInt")
    bounded_int1 = simple_bounded_type(5)
    bounded_int2 = simple_bounded_type(3)
    result =  bounded_int2 - bounded_int1  # 3 - 5 = -2, что меньше min_value=0
    assert not result.is_OK