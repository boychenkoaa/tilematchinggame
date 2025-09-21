from abc import ABC, abstractmethod
from typing import List
from contract import Contract
from combinations import RC
from base import RowInt, ColInt
from simple_game import SimpleGame, SimpleGameFactory

# Добавить определение типа:
CLIArgs = List[str]

class Command(ABC, Contract):
    description = "Абстрактная команда."
    
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def deserialize(self, args: CLIArgs) -> None:
        pass


class GameCommand(Command):
    description = "Абстрактная игровая команда."
    ERR_INVALID_ARGS_COUNT = "Неверное число аргументов"
    ERR_INVALID_ARGS_TYPE = "Неверный тип аргументов"
    
    @abstractmethod
    def visit(self, game: SimpleGame) -> None:  # Исправлено: было visit
        """Выполняет команду."""
        pass

class SwapCommand(GameCommand):
    """Команда обмена двух элементов."""
    description = "Обменять два элемента: swap <row1> <col1> <row2> <col2>"
    
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда swap требует 4 аргумента: swap <row1> <col1> <row2> <col2>"
    ERR_INVALID_ARGS_TYPE = "Все аргументы команды swap должны быть числами"
    
    def __init__(self):
        super().__init__()
        self.row1 = None
        self.col1 = None
        self.row2 = None
        self.col2 = None
    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 4, self.ERR_INVALID_ARGS_COUNT)
        self.row1 = int(args[0])
        self.col1 = int(args[1])
        self.row2 = int(args[2])
        self.col2 = int(args[3])
        
    def visit(self, game: SimpleGame) -> None:
        game.smart_swap_move(RC(RowInt(self.row1), ColInt(self.col1)), RC(RowInt(self.row2), ColInt(self.col2)))

class EraseAllCommand(GameCommand):
    """Команда удаления всех элементов."""
    description = "Удалить все элементы: erase_all"
    
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда erase_all не принимает аргументов"

    def __init__(self):
        super().__init__()

    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 0, self.ERR_INVALID_ARGS_COUNT)
        
    
    def visit(self, game: SimpleGame) -> None:
        game.erase_all_move()

class EraseRowCommand(GameCommand):
    """Команда удаления строки."""
    
    description = "Удалить строку: erase_row <row>"
    
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда erase_row требует 1 аргумент: erase_row <row>"
    ERR_INVALID_ARGS_TYPE = "Аргумент команды erase_row должен быть числом"
    
    def __init__(self):
        super().__init__()
        self.row = None
    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 1 and args[0].isdigit(), self.ERR_INVALID_ARGS_COUNT)
        self.row = int(args[0])
    
    @Contract.on
    def visit(self, game: SimpleGame) -> None:  
        game.erase_row_move(RC(RowInt(self.row), ColInt(0)))


class EraseColCommand(GameCommand):
    """Команда удаления столбца."""
    # Переменные класса
    description = "Удалить столбец: erase_col <col>"
    
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда erase_col требует 1 аргумент: erase_col <col>"
    ERR_INVALID_ARGS_TYPE = "Аргумент команды erase_col должен быть числом"
    
    def __init__(self):
        super().__init__()
        self.col = None
    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 1 and args[0].isdigit(), self.ERR_INVALID_ARGS_COUNT)
        self.col = int(args[0])
    
    @Contract.on
    def visit(self, game: SimpleGame) -> None:
        game.erase_col_move(RC(RowInt(0), ColInt(self.col)))

class EraseCrossCommand(GameCommand):
    """Команда удаления креста."""
    
    description = "Удалить крест: erase_cross <row> <col>"
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда erase_cross требует 2 аргумента: erase_cross <row> <col>"
    ERR_INVALID_ARGS_TYPE = "Аргументы команды erase_cross должны быть числами"
    @Contract.on
    def visit(self, game: SimpleGame) -> None:
        game.erase_cross_move(RC(RowInt(self.row), ColInt(self.col)))
    
    def __init__(self):
        super().__init__()
        self.row = None
        self.col = None
    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 2, self.ERR_INVALID_ARGS_COUNT)
        self.check_pre(args[0].isdigit() and args[1].isdigit(), self.ERR_INVALID_ARGS_TYPE)
        self.row = int(args[0])
        self.col = int(args[1])
        
    def visit(self, game: SimpleGame) -> None:
        return game.erase_cross_move(RC(RowInt(self.row), ColInt(self.col)))

class ShuffleCommand(GameCommand):
    """Команда перемешивания поля."""
    
    description = "Перемешать поле: shuffle"
    
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда shuffle не принимает аргументов"
    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 0, self.ERR_INVALID_ARGS_COUNT)
    
    @Contract.on
    def visit(self, game: SimpleGame) -> None:
        game.shuffle_move()


class RestartCommand(GameCommand):
    """Команда перезапуска игры."""
    
    description = "Перезапустить игру: restart"
    
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда restart не принимает аргументов"
    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 0, self.ERR_INVALID_ARGS_COUNT)
    
    @Contract.on
    def visit(self, game: SimpleGame) -> None:
        game.from_other(SimpleGameFactory.create_game())

class SwapBonusCommand(GameCommand):
    """Команда обмена бонусом."""
    description = "Обмен бонусом: swap_bonus <row> <col>"
    
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда swap_bonus требует 4 аргумента: swap_bonus <row1> <col1> <row2> <col2>"
    ERR_INVALID_ARGS_TYPE = "Все аргументы команды swap_bonus должны быть числами"
    
    def __init__(self):
        super().__init__()
        self.row1 = None
        self.col1 = None
        self.row2 = None
        self.col2 = None
    
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 4, self.ERR_INVALID_ARGS_COUNT)
        self.check_pre(args[0].isdigit() and args[1].isdigit() and args[2].isdigit() and args[3].isdigit(), self.ERR_INVALID_ARGS_TYPE)
        self.row1 = int(args[0])
        self.col1 = int(args[1])
        self.row2 = int(args[2])
        self.col2 = int(args[3])
    
    @Contract.on
    def visit(self, game: SimpleGame) -> None:
        game.swap_bonus_move(RC(RowInt(self.row1), ColInt(self.col1)), RC(RowInt(self.row2), ColInt(self.col2)))

class BrushCommand(GameCommand):
    description = "Команда удаления по цвету камня: brush <row> <col>"
    
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда brush требует 2 аргумента: brush <row> <col>"
    ERR_INVALID_ARGS_TYPE = "Все аргументы команды brush должны быть числами"
    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 2, self.ERR_INVALID_ARGS_COUNT)
        self.check_pre(args[0].isdigit() and args[1].isdigit(), self.ERR_INVALID_ARGS_TYPE)
        self.row = int(args[0])
        self.col = int(args[1])
    
    @Contract.on
    def visit(self, game: SimpleGame) -> None:
        game.brush_move(RC(RowInt(self.row), ColInt(self.col)))

class AutoSwapCommand(GameCommand):
    """Команда автоматического хода обменом"""
    description = "Автоматический обмен бонусом: auto_swap"
    
    # Сообщения об ошибках
    ERR_INVALID_ARGS_COUNT = "Команда auto_swap не принимает аргументов"
    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(len(args) == 0, self.ERR_INVALID_ARGS_COUNT)
    
    @Contract.on
    def visit(self, game: SimpleGame) -> None:
        game.auto_swap_move()