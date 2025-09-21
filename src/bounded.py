from __future__ import annotations
from functools import total_ordering
from typing import Generic, TypeVar, Literal, Union, overload, ClassVar, Optional, Type, cast
from contract import Contract
import types

import contract

# TypeVar для значений в определенном диапазоне
T = TypeVar('T', bound=int)

@total_ordering
class BoundedInt(Generic[T], Contract):
    # Параметры класса для границ значений
    min_value: int = 0
    max_value: int = 0
    
    @Contract.on
    def __init__(self, initial_value: int):
        super().__init__()
        # Проверка значения при инициализации
        self.check_pre(isinstance(initial_value, int) and \
            initial_value >= self.min_value and \
            initial_value <= self.max_value, "Initial value is out of Bounds")
        self._value = initial_value
    
    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    @Contract.on
    def value(self, new_value: int) -> None:
        # Проверка значения при изменении
        self.check_pre(isinstance(new_value, int) and \
            new_value >= self.min_value and \
            new_value <= self.max_value, "New value is out of Bounds")

        self._value = new_value
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value})"
    
    def __eq__(self, other: BoundedInt[T] | int) -> bool:
        if isinstance(other, BoundedInt):
            return self._value == other._value
        return self._value == other
    
    def __int__(self) -> int:
        return self._value
    
    def __add__(self, other: BoundedInt[T]) -> BoundedInt[T]:
        return self.__class__(self._value + other._value)
    
    def __sub__(self, other: BoundedInt[T]) -> BoundedInt[T]:
        return self.__class__(self._value - other._value)
    
    def __mul__(self, other: BoundedInt[T]) -> BoundedInt[T]:
        return self.__class__(self._value * other._value)

    def __lt__(self, other: BoundedInt[T]) -> bool:
        return self._value < other.value
    
    # Фабричный метод для создания специализированных классов
    @classmethod
    def create_bounded_type(cls, min_val: int, max_val: int, name: Optional[str] = None) -> Type[BoundedInt[T]]:
        if min_val > max_val:
            raise ValueError(f"min_value ({min_val}) must be less than or equal to max_value ({max_val})")
        
        # Создаем новый класс с заданными границами
        class_name = name or f"BoundedInt_{min_val}_{max_val}"
        
        new_class = types.new_class(class_name, (BoundedInt,), {}, lambda ns: ns.update({
            'min_value': min_val,
            'max_value': max_val
        }))
        
        return cast(Type[BoundedInt[T]], new_class)


'''
# Примеры использования от нейросетки

# 1. Создание специализированного типа для координат доски
BoardCoordinate = BoundedInt.create_bounded_type(0, WIDTH-1, "BoardCoordinate")
# 2. Создание типа для процентов
Percentage = BoundedInt.create_bounded_type(0, 100, "Percentage")
# 3. Создание типа для оценок
Grade = BoundedInt.create_bounded_type(1, 5, "Grade")
'''
