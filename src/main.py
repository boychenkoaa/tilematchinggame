from cli import GameCLI
from simple_game import SimpleGameFactory

def main():
    game = SimpleGameFactory.create_game()
    cli = GameCLI(game)
    cli.run_interactive()


if __name__ == "__main__":
    main()