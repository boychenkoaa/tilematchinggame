from __future__ import annotations
from typing import List
from contract import Contract
from base import Printer
from simple_game import SimpleGame
from commands import (
    Command, GameCommand, EraseAllCommand, AutoSwapCommand,
    SwapCommand, EraseRowCommand, EraseColCommand, SwapBonusCommand,
    EraseCrossCommand, ShuffleCommand, RestartCommand, BrushCommand
)

CLIArgs = List[str]


class CLICommand(Command):
    description = "Абстрактная CLI команда."
    ERR_INVALID_ARGS = "Некорректные значения аргументов."
    
    @Contract.on
    def deserialize(self, args: CLIArgs) -> None:
        self.check_pre(True)
        pass
    
    def visit(self, cli: GameCLI) -> None:
        pass
    
class HelpCommand(CLICommand):
    """Команда показа справки."""
    
    def visit(self, cli: 'GameCLI') -> None:
        """Показывает справку по командам."""
        aliases_reversed = {}
        for k, v in cli.COMMAND_ALIASES.items():
            if aliases_reversed.get(v) is None:
                aliases_reversed[v] = [k]
            else:
                aliases_reversed[v].append(k)
        
        print(cli.MSG_AVAILABLE_COMMANDS)
        for command_name, command in cli.GAME_COMMANDS.items():
            print(f"  {command.description}  ({' '.join(aliases_reversed.get(command_name, []))})")
        print(cli.MSG_HELP_COMMAND)
        print(cli.MSG_EXIT_COMMAND)


class ExitCommand(CLICommand):
    """Команда выхода из игры."""
    
    def visit(self, cli: 'GameCLI') -> None:
        """Завершает игру."""
        print(cli.MSG_GOODBYE)
        cli.stop()

class SwitchPrintSubstepsCommand(CLICommand):
    """Команда переключения печати подшагов."""
    description = "Переключить печать подшагов: switch_print_substeps"

    def visit(self, cli: 'GameCLI') -> None:
        """Переключает печать подшагов."""
        if Printer.is_steps_on():
            Printer.steps_off()
        else:
            Printer.steps_on()
        print(f"Печать подшагов {'включена' if Printer.is_steps_on() else 'выключена'}")

class CLIBase:
    """Константы для CLI интерфейса."""
    MSG_UNKNOWN_COMMAND = "Неизвестная команда: {}. Введите 'help' для справки."
    MSG_EXECUTION_ERROR = "Ошибка выполнения команды '{}': {}"
    MSG_SERIALIZATION_ERROR = "Ошибка сериализации команды (неверные аргументы или их количество) '{}': {}"
    MSG_GAME_OVER = "Игра завершена!"
    MSG_AVAILABLE_COMMANDS = "Доступные команды:"
    MSG_GOODBYE = "До свидания!"
    MSG_WELCOME = "Введите 'help' для списка команд или 'exit' для выхода"
    MSG_HELP_COMMAND = "  Показать справку: help (h, ?)"
    MSG_EXIT_COMMAND = "  Выйти из игры: exit (quit, q)"
    MSG_INVALID_COMMAND = "Неверный формат команды. Введите 'help' для справки."
    
    # Словарь алиасов команд
    COMMAND_ALIASES = {
        's': 'swap',
        'er': 'erase_row', 
        'ec': 'erase_col',
        'ex': 'erase_cross',
        'ea': 'erase_all',
        'sb': 'swap_bonus',
        'sh': 'shuffle',
        'r': 'restart',
        'b': 'brush',
        'sw': 'switch',
        'a': 'auto_swap',
        # Алиасы для встроенных команд CLI
        'h': 'help',
        '?': 'help',
        'quit': 'exit',
        'q': 'exit'
    }
    
    GAME_COMMANDS = {
        'swap': SwapCommand(),
        'swap_bonus': SwapBonusCommand(),
        'erase_all': EraseAllCommand(),
        'erase_row': EraseRowCommand(),
        'auto_swap': AutoSwapCommand(),
        'erase_col': EraseColCommand(),
        'erase_cross': EraseCrossCommand(),
        'shuffle': ShuffleCommand(),
        'brush': BrushCommand(),
        'restart': RestartCommand()        
    }
 
    CLI_COMMANDS = {
        'help': HelpCommand(),
        'exit': ExitCommand(),
        'switch': SwitchPrintSubstepsCommand()
    }
    
class GameCLI(Contract, CLIBase):
    """Интерфейс командной строки для игры."""
    
    def __init__(self, game: SimpleGame) -> None:
        super().__init__()
        self._is_running = True
        self._game: SimpleGame = game
    
    def stop(self):
        self._is_running = False
    
    def _resolve_command_name(self, command_name: str) -> str:
        """Преобразует алиас в полное имя команды."""
        return self.COMMAND_ALIASES.get(command_name, command_name)
    
    @Contract.on
    def execute(self, command_line: str) -> None:
        """Выполняет команду из строки."""
        parts = command_line.strip().split()
        self.check_pre(len(parts) > 0, self.MSG_INVALID_COMMAND)
        
        command_name = parts[0].lower()
        args = parts[1:]
        
        # Преобразуем алиас в полное имя команды
        resolved_name = self._resolve_command_name(command_name)
        
        # Проверяем CLI команды
        if resolved_name in self.CLI_COMMANDS:
            cli_command = self.CLI_COMMANDS[resolved_name]
            cli_command.deserialize(args)
            self.check_pre(cli_command.is_OK, self.MSG_SERIALIZATION_ERROR.format(resolved_name,args))
            self.accept(cli_command)
            return
        
        # Проверяем игровые команды
        if resolved_name in self.GAME_COMMANDS:
            game_command: Command = self.GAME_COMMANDS[resolved_name]
            game_command.deserialize(args)
            self.check_pre(game_command.is_OK, self.MSG_SERIALIZATION_ERROR.format(resolved_name,args))
            self._game.accept(game_command)
            if not self._game.is_OK:
                print(self._game.message)
            return
        
        print(self.MSG_UNKNOWN_COMMAND.format(command_name))
    
    def accept(self, command: CLICommand) -> None:
        """Принять команду."""
        command.visit(self)
    
    def run_interactive(self) -> None:
        """Запускает интерактивный режим."""
        print(self.MSG_WELCOME)
        print(self._game)
        while self._is_running:
            command_line = input("> ")
            self.execute(command_line)
            if self._game.is_gameover:
                print(self.MSG_GAME_OVER)
                print(self._game)
                self._is_running = False
                input("Нажмите Enter для выхода")
                
            
            


