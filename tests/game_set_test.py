import unittest
from unittest.mock import patch
import json
import random
from dawg import DAWG
import findmatchingwords
from game_set import GameSet

class TestGameSet(unittest.TestCase):

    @patch('findmatchingwords.find_matching_words')
    def test_computer_move_with_blank_tile(self, mock_find_matching_words):
        # Create a fake dictionary and mock matching words
        mock_find_matching_words.return_value = {'rave'}

        # Create a simple dictionary (DAWG)
        dictionary_path = "collins2019.txt"
        word_dictionary = DAWG(dictionary_path)

        # Initialize game set with a mock dictionary and fixed tiles
        game = GameSet(dictionary=word_dictionary, board_name='Standard', language_descriptor='en-us', num_players=2)
        game.players['Player 1']['tiles'] = ['R', 'A', '?', 'E', 'B', 'C', 'D']
        game.players['Player 1']['is_computer'] = True

        # Perform the computer move
        game.computer_move('Player 1')

        # Check the state of the board and the player's rack
        center_row = len(game.board) // 2
        center_col = len(game.board[0]) // 2
        self.assertEqual(game.board[center_row][center_col:center_col+4], ['R', 'A', '?', 'E'])
        self.assertNotIn('R', game.players['Player 1']['tiles'])
        self.assertNotIn('A', game.players['Player 1']['tiles'])
        self.assertNotIn('E', game.players['Player 1']['tiles'])

    @patch('builtins.input', side_effect=['RA?E'])
    def test_human_move_with_blank_tile(self, mock_input):
        # Create a simple dictionary (DAWG)
        dictionary_path = "collins2019.txt"
        word_dictionary = DAWG(dictionary_path)

        # Initialize game set with a mock dictionary and fixed tiles
        game = GameSet(dictionary=word_dictionary, board_name='Standard', language_descriptor='en-us', num_players=2)
        game.players['Player 1']['tiles'] = ['R', 'A', '?', 'E', 'B', 'C', 'D']

        # Perform the human move
        game.human_move('Player 1')

        # Check the state of the board and the player's rack
        center_row = len(game.board) // 2
        center_col = len(game.board[0]) // 2
        self.assertEqual(game.board[center_row][center_col:center_col+4], ['R', 'A', '?', 'E'])
        self.assertNotIn('R', game.players['Player 1']['tiles'])
        self.assertNotIn('A', game.players['Player 1']['tiles'])
        self.assertNotIn('E', game.players['Player 1']['tiles'])

if __name__ == "__main__":
    unittest.main()
