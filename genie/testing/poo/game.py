from player import Player

# Player class

class Game:
    def __init__(self):
        self.player = None

    def start_game(self):
        player_name = input('Enter your name: ')
        self.player = Player(player_name)
        self.player.display_status()

    def process_input(self, user_input):
        if user_input == '1':
            print('You chose option 1')
        elif user_input == '2':
            print('You chose option 2')
        else:
            print('Invalid choice')

    def update_game_state(self):
        if self.player.hp > 0:
            if self.player.hp > 10:
                self.player.hp -= 10
            else:
                self.player.hp = 0
        else:
            print('Game over')

    def display_game_state(self):
        # TODO: Implement game state display logic
        pass

    def check_game_over(self):
        if self.player.hp <= 0:
            print('Game over')
            return True
        return False

    def check_game_win(self):
        if 'loot' in self.player.inventory:
            print('You found the loot! You win!')
            return True
        return False


if __name__ == '__main__':
    game = Game()
    game.start_game()

    while True:
        user_input = input('Enter your choice: ')
        game.process_input(user_input)

        if game.check_game_over():
            break

        game.update_game_state()
        game.display_game_state()

        if game.check_game_win():
            break
