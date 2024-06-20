import json
import random
from dawg import DAWG
import findmatchingwords

class GameSet:
    """Represents a game set including board, tiles, and players."""

    COLOR_RESET = "\033[0m"
    COLOR_LIGHT_BLUE = "\033[94m"
    COLOR_DARK_BLUE = "\033[34m"
    COLOR_LIGHT_RED = "\033[91m"
    COLOR_DARK_RED = "\033[31m"
    COLOR_WHITE = "\033[97m"
    COLOR_DARK_GREY = "\033[90m"

    def __init__(self, dictionary: DAWG, board_name: str = 'Standard', language_descriptor: str = 'en-us', num_players: int = 2, board_file: str = 'boards.json', tile_file: str = 'tiles.json'):
        """Initializes the game set with the given board and language settings."""
        if num_players not in [2, 3, 4]:
            raise ValueError("Number of players must be 2, 3, or 4.")

        self.dictionary = dictionary
        self.tiles = self.load_tiles(language_descriptor, tile_file)
        self.board, self.special_cells = self.load_board(board_name, board_file)
        self.stock = self.initialize_stock()
        self.players = {f'Player {i+1}': {'tiles': [], 'is_computer': False} for i in range(num_players)}
        self.draw_initial_tiles()
        self.assign_computer_players()
        self.start_game()

    def load_tiles(self, language_descriptor: str, tile_file: str) -> dict:
        """Loads tile data for the specified language descriptor from the tile file."""
        try:
            with open(tile_file, 'r') as f:
                tile_sets = json.load(f)
                for tile_set in tile_sets.values():
                    if language_descriptor in tile_set['languages']:
                        return tile_set['tiles']
            raise ValueError(f"No tile set found for language descriptor: {language_descriptor}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Tile file '{tile_file}' not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from tile file '{tile_file}'.")

    def load_board(self, board_name: str, board_file: str) -> tuple:
        """Loads board configuration and special cells from the board file."""
        try:
            with open(board_file, 'r') as f:
                boards = json.load(f)
                if board_name not in boards:
                    raise ValueError(f"Board '{board_name}' not found in board file.")
                board_config = boards[board_name]
                width = board_config['width']
                height = board_config['height']
                board = [['' for _ in range(width)] for _ in range(height)]
                special_cells = {tuple(map(int, k.split(','))): v for k, v in board_config['special_cells'].items()}
                return board, special_cells
        except FileNotFoundError:
            raise FileNotFoundError(f"Board file '{board_file}' not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from board file '{board_file}'.")

    def initialize_stock(self) -> list:
        """Initializes the stock of tiles."""
        stock = []
        for tile, info in self.tiles.items():
            stock.extend([tile] * info['count'])
        random.shuffle(stock)
        return stock

    def draw_tiles(self, num_tiles: int) -> list:
        """Draws a specified number of tiles from the stock."""
        drawn_tiles = [self.stock.pop() for _ in range(num_tiles) if self.stock]
        return drawn_tiles

    def draw_initial_tiles(self):
        """Draws initial tiles for all players."""
        for player in self.players:
            self.players[player]['tiles'] = self.draw_tiles(7)

    def assign_computer_players(self):
        """Randomly assigns one or more players as computer players."""
        num_computer_players = random.randint(1, len(self.players) - 1)
        computer_players = random.sample(list(self.players.keys()), num_computer_players)
        for player in computer_players:
            self.players[player]['is_computer'] = True

    def start_game(self):
        """Starts the game by choosing a random player to begin."""
        starting_player = random.choice(list(self.players.keys()))
        print(f"{starting_player} starts the game!")
        self.display_game_state()
        if self.players[starting_player]['is_computer']:
            self.computer_move(starting_player)
        else:
            self.human_move(starting_player)

    def display_board(self):
        """Displays the board with tiles and special cells."""
        for row in range(len(self.board)):
            row_display = ''
            for col in range(len(self.board[row])):
                cell = self.board[row][col]
                if cell:
                    # Handle blank tiles which have no points
                    if cell == "?":
                        row_display += f' {self.COLOR_WHITE}?{self.COLOR_RESET} '
                    else:
                        try:
                            tile_value = self.tiles[cell]['points']
                            if tile_value < 10:
                                row_display += f' {self.COLOR_WHITE}{cell}{self.COLOR_DARK_GREY}{tile_value}{self.COLOR_RESET}'
                            else:
                                tile_value_str = str(tile_value)
                                row_display += f'{self.COLOR_DARK_GREY}{tile_value_str[0]}{self.COLOR_WHITE}{cell}{self.COLOR_DARK_GREY}{tile_value_str[1]}{self.COLOR_RESET}'
                        except KeyError as e:
                            print(f"Error: Tile '{cell}' not found in tiles dictionary.")
                else:
                    if (row, col) in self.special_cells:
                        special = self.special_cells[(row, col)]
                        if special == '2L':
                            row_display += f' {self.COLOR_LIGHT_BLUE}2{self.COLOR_RESET} '
                        elif special == '3L':
                            row_display += f' {self.COLOR_DARK_BLUE}3{self.COLOR_RESET} '
                        elif special == '2W':
                            row_display += f' {self.COLOR_LIGHT_RED}2{self.COLOR_RESET} '
                        elif special == '3W':
                            row_display += f' {self.COLOR_DARK_RED}3{self.COLOR_RESET} '
                    else:
                        row_display += ' . '
            print(row_display)

    def display_players_racks(self):
        """Displays the tiles of all players."""
        for player, player_data in self.players.items():
            print(f"{player} (Computer: {player_data['is_computer']}): {' '.join(player_data['tiles'])}")

    def display_game_state(self):
        """Displays the board and the tiles of all players."""
        self.display_board()
        self.display_players_racks()

    def place_tile(self, tile: str, row: int, col: int):
        """Places a tile on the board at the specified position."""
        if 0 <= row < len(self.board) and 0 <= col < len(self.board[0]):
            if not self.board[row][col]:
                self.board[row][col] = tile
            else:
                print("Cell is already occupied.")
        else:
            print("Invalid board position.")

    def computer_move(self, player: str):
        """Handles the computer player's move."""
        self.display_game_state()
        print(f"{player} (computer) is making a move...")
        center_row = len(self.board) // 2
        center_col = len(self.board[0]) // 2
        char_list = self.players[player]['tiles']
        pattern = "?"

        matching_words = findmatchingwords.find_matching_words(pattern, char_list, self.dictionary)
        matching_words_list = [word.upper() for word in matching_words]  # Convert words to uppercase

        if matching_words_list:
            chosen_word = random.choice(matching_words_list)
            for i, tile in enumerate(chosen_word):
                if tile == "?":
                    # Find a blank tile from the player's rack to use
                    blank_tile_index = self.players[player]['tiles'].index("?")
                    self.players[player]['tiles'].pop(blank_tile_index)
                    # Place the tile as a blank
                    self.place_tile("?", center_row, center_col + i)
                else:
                    if 0 <= center_col + i < len(self.board[0]):
                        self.place_tile(tile, center_row, center_col + i)
                        if tile in self.players[player]['tiles']:
                            self.players[player]['tiles'].remove(tile)
            # Draw new tiles to replace the used ones
            self.players[player]['tiles'].extend(self.draw_tiles(len(chosen_word)))
        else:
            print("No valid moves for the computer.")

        self.display_board()

    def human_move(self, player: str):
        """Handles the human player's move."""
        self.display_game_state()
        print(f"{player} (human), it's your turn!")
        while True:
            word = input("Enter a word to place: ").strip().upper()
            if all(tile in self.players[player]['tiles'] or tile == "?" for tile in word):
                break
            print("You do not have all the tiles to form this word. Try again.")

        center_row = len(self.board) // 2
        center_col = len(self.board[0]) // 2

        for i, tile in enumerate(word):
            if tile == "?":
                # Find a blank tile from the player's rack to use
                blank_tile_index = self.players[player]['tiles'].index("?")
                self.players[player]['tiles'].pop(blank_tile_index)
                # Place the tile as a blank
                self.place_tile("?", center_row, center_col + i)
            else:
                if 0 <= center_col + i < len(self.board[0]):
                    self.place_tile(tile, center_row, center_col + i)
                    if tile in self.players[player]['tiles']:
                        self.players[player]['tiles'].remove(tile)

        # Draw new tiles to replace the used ones
        self.players[player]['tiles'].extend(self.draw_tiles(len(word)))
        self.display_board()

if __name__ == "__main__":
    dictionary_path = "collins2019.txt"
    word_dictionary = DAWG(dictionary_path)

    game = GameSet(dictionary=word_dictionary, board_name='Standard', language_descriptor='en-us', num_players=2)

    game.display_game_state()

    # Display players' tiles
    for player, player_data in game.players.items():
        print(f"{player} (Computer: {player_data['is_computer']}): {' '.join(player_data['tiles'])}")
