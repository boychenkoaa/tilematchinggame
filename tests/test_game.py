import pytest
from copy import deepcopy
from base import Stone, Bonus, RC, RowInt, ColInt
from cells import BonusChest, Statistics
from combinations import Mask
from game_board import Board, GameBoard
from simple_game import SimpleGame, SimpleGameFactory
from commands import GameCommand


class TestGame:
    """Тесты для класса Game."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.game = SimpleGameFactory.create_test_game()
    
    def test_init(self):
        """Тест инициализации игры."""
        board = Board()
        bonus_chest = BonusChest()
        statistics = Statistics()
        game_board = GameBoard(board, bonus_chest, statistics)
        game = SimpleGame(game_board)
        
        assert game._game_board is game_board
        assert not game.is_print_substeps
    
    def test_set_is_print_substeps(self):
        """Тест установки флага печати подшагов."""
        assert not self.game.is_print_substeps
        
        self.game.set_is_print_substeps(True)
        assert self.game.is_print_substeps
        
        self.game.set_is_print_substeps(False)
        assert not self.game.is_print_substeps
    
    def test_from_other(self):
        """Тест копирования состояния из другой игры."""
        other_game = SimpleGameFactory.create_test_game()
        other_game.set_is_print_substeps(True)
        
        # Изменяем состояние другой игры
        other_game._game_board._chest.add_bonus(Bonus.CROSS)
        
        # Копируем состояние
        self.game.from_other(other_game)
        
        assert self.game.is_print_substeps
        assert self.game._game_board is not other_game._game_board  # Должна быть копия
    
    def test_moves(self):
        ...


    def test_accept_command(self):
        """Тест принятия команды."""
        # Создаем простую тестовую команду
        class TestCommand(GameCommand):
            def __init__(self):
                self.executed = False
            
            def execute(self, game: SimpleGame):
                self.executed = True
        
        command = TestCommand()
        self.game.accept(command)
        
        assert command.executed


class TestGameFactory:
    """Тесты для фабрики игр."""
    
    def test_create_game(self):
        """Тест создания игры по умолчанию."""
        game = SimpleGameFactory.create_game()
        
        assert isinstance(game, SimpleGame)
        assert isinstance(game._game_board, GameBoard)
        assert isinstance(game._game_board._board, Board)
        assert isinstance(game._game_board._chest, BonusChest)
        assert isinstance(game._game_board._statistics, Statistics)
        
        # Проверяем, что поле заполнено начальными значениями
        assert not game._game_board.has_empty_cells()
    
    def test_create_test_game(self):
        """Тест создания тестовой игры."""
        game = SimpleGameFactory.create_test_game()
        
        assert isinstance(game, SimpleGame)
        # Тестовая игра должна быть идентична обычной
        regular_game = SimpleGameFactory.create_game()
        
        # Сравниваем типы компонентов
        assert type(game._game_board) == type(regular_game._game_board)
        assert type(game._game_board._board) == type(regular_game._game_board._board)