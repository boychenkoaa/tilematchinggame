from __future__ import annotations
from random import random, choice, randint
from copy import deepcopy
from typing import Callable
from game_board import GameBoard, Bonus, EraseMaskBonus, ERASE_BONUS_MASKS, Board
from combinations import RC, Mask
from contract import Contract
from base import RowInt, ColInt, Printer, PrinterConstants
from cells import BonusChest, Statistics

class SimpleGame(Contract):
    """Игровая логика с ходами и бонусами."""
    def __init__(self, game_board: GameBoard):
        self._game_board = game_board
        self._is_print_substeps = False
        
    # запросы
    # TODO -- тоже криво, по уму нужно General и Any
    @property
    def is_print_substeps(self) -> bool:
        return self._is_print_substeps
        
    # КОМАНДЫ
    def set_is_print_substeps(self, value: bool):
        """Устанавливает значение для печати подшагов при стабилизации."""
        self._is_print_substeps = value
        
    def from_other(self, other: SimpleGame):
        self._game_board = deepcopy(other._game_board)
        self._is_print_substeps = other._is_print_substeps
    
   
    def bonus_move(bonus: Bonus):
        """Декоратор для ходов с использованием бонусов."""
        def decorator(func: Callable) -> Callable:
            @Contract.on
            def inner(self, *args, **kwargs):
                self.check_pre(self._game_board.can_use_bonus(bonus), f"Нет бонусов {bonus}")
                self._game_board.use_bonus(bonus)  
                result = func(self, *args, **kwargs)
                self._game_board.process()
                print("current:\n",self._game_board, sep="")
                return result
            return inner
        return decorator
    
    @Contract.on
    @Printer.on("Board", PrinterConstants.PRINT_BOARD_FLAG)
    def smart_swap_move(self, rc1: RC, rc2: RC) -> None:
        """Ход обмена двух элементов."""
        is_correct = self._game_board.is_smart_swap_correct(rc1, rc2)
        self.check_pre(is_correct, f"Некорректный ход обмена {rc1} {rc2}")
        self._game_board.smart_swap(rc1, rc2)
        self._game_board.process()
    
    @Contract.on
    @Printer.on("Board", PrinterConstants.PRINT_BOARD_FLAG)
    def auto_swap_move(self) -> None:
        """Автоматический ход обменом."""
        self.check_pre(self._game_board.has_smart_swap, "Нет возможных ходов обмена")
        rc1, rc2 = self._game_board.find_smart_swap()
        self._game_board.smart_swap(rc1, rc2)
        self._game_board.process()

    @bonus_move(Bonus.ROW)
    def erase_row_move(self, rc: RC) -> None:
        """Ход удаления строки."""
        mask_raw = ERASE_BONUS_MASKS[EraseMaskBonus.ROW]
        mask = Mask().from_raw(rc.raw_repr, mask_raw)
        self._game_board.erase_mask(mask)

    @bonus_move(Bonus.COL)
    def erase_col_move(self, rc: RC) -> None:
        """Ход удаления столбца."""
        mask_raw = ERASE_BONUS_MASKS[EraseMaskBonus.COL]
        mask = Mask().from_raw(rc.raw_repr, mask_raw)
        self._game_board.erase_mask(mask)

    @bonus_move(Bonus.ALL)
    def erase_all_move(self) -> None:
        """Ход удаления всего поля."""
        mask_raw = ERASE_BONUS_MASKS[EraseMaskBonus.ALL]
        mask = Mask().from_raw((0, 0), mask_raw)
        self._game_board.erase_mask(mask)

    @bonus_move(Bonus.CROSS)
    def erase_cross_move(self, rc: RC) -> None:
        """Ход удаления креста (строка + столбец)."""
        mask_raw = ERASE_BONUS_MASKS[EraseMaskBonus.CROSS]
        mask = Mask()
        mask.from_raw(rc.raw_repr, mask_raw)
        self._game_board.erase_mask(mask)

    @bonus_move(Bonus.BRUSH)
    def brush_move(self, rc: RC) -> None:
        """Ход кисти."""
        mask = self._game_board.brush_mask(rc)
        self._game_board.erase_mask(mask)

    @bonus_move(Bonus.SWAP)
    def swap_bonus_move(self, rc1: RC, rc2: RC) -> None:
        """Ход обмена с бонусом."""
        self._game_board.swap(rc1, rc2)
        
    @bonus_move(Bonus.SHUFFLE)
    def shuffle_move(self) -> None:
        """Ход перемешивания поля."""
        self._game_board.shuffle()
    
    @property
    def is_gameover(self) -> bool:
        return not self._game_board.has_smart_swap and self._game_board.is_chest_empty
    
    def accept(self, command: 'GameCommand') -> None:
        """Принять команду."""
        command.visit(self)
        
    def __str__(self):
        return str(self._game_board)
    
    def __repr__(self) -> str:
        return str(self)


class SimpleGameFactory:
    """Фабрика для создания игровых компонентов."""
    
    @staticmethod
    def create_game() -> SimpleGame:
        """игра по умолчанию"""
        initian_cells = [
            "ABCDEABC",
            "BCDEABCD",
            "CDEABCDE",
            "DEACBDEA",
            "ABABABAB",
            "BABABABA",
            "CDCDCDCD",
            "DCDCDCDC"            
        ]
        board = Board()
        board.from_raw(initian_cells)
        bonus_chest = BonusChest()
        for i in range(15):
            bonus_chest.add_bonus(choice(list(Bonus)))
        statistics = Statistics()
        game_board = GameBoard(board, bonus_chest, statistics)
        return SimpleGame(game_board)
    
    @staticmethod
    def create_test_game() -> SimpleGame:
        """для тестов"""
        return SimpleGameFactory.create_game()


    @staticmethod
    def create_final_game() -> SimpleGame:
        """финальная игра"""
        initian_cells = [
            "ABCDEFGH",
            "BCDEFGHA",
            "CDEFGHAB",
            "DEFGHABC",
            "EFGHABCD",
            "FGHABCDE", 
            "GHABCDEF",
            "HABCDEFG"
        ]
        board = Board()
        board.from_raw(initian_cells)
        bonus_chest = BonusChest()
        statistics = Statistics()
        game_board = GameBoard(board, bonus_chest, statistics)
        return SimpleGame(game_board)

if __name__ == "__main__":
    stones_str_list = [
        "BACDEABC",  # B в (0,0)
        "ACDEABCD",  # A в (1,0) 
        "ACDEABCD",  # A в (2,0)
        "CDEABCDE",
        "DEABCDEA",
        "EABCDEAB", 
        "ABCDEABC",
        "BCDEABCD"
    ]
    board = Board()
    board.from_raw(stones_str_list)
    
    bonus_chest = BonusChest()
    for bonus in Bonus:
        bonus_chest.add_bonus(bonus)
        bonus_chest.add_bonus(bonus)
    statistics = Statistics()
    game_board = GameBoard(board, bonus_chest, statistics)
    game = SimpleGame(game_board)
    game.set_is_print_substeps(True)
    rc_list = [RC(RowInt(randint(0, board.height.value - 1)), ColInt(randint(0, board.width.value - 1))) for _ in range(6)] 
    
    print("\nbrush -> " + str(rc_list[0].raw_repr))
    game.brush_move(rc_list[0])
    
    print("\nerase_all -> ")
    game.erase_all_move()

    print("\nerase_col -> " + str(rc_list[1].raw_repr))
    game.erase_col_move(rc_list[1])

    print("\nerase_row -> " + str(rc_list[2].raw_repr))
    game.erase_row_move(rc_list[2])

    print("\nerase_cross -> " + str(rc_list[3].raw_repr))
    game.erase_cross_move(rc_list[3])

    print("\nswap_move -> " + str(rc_list[4].raw_repr) + "," + str(rc_list[5].raw_repr))
    game.swap_bonus_move(rc_list[4], rc_list[5])

    print("\nshuffle")
    game.shuffle_move()


