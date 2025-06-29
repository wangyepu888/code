from Game import Game, Type
from Token import Token
import numpy as np

class GameAgent:
    def __init__(self, token: Token):
        """
        Initialize the agent with its assigned token (X or O).
        """
        self._token = token

    def token(self):
        return self._token

    def make_move(self, game: Game):
        """
        This is the main driver of the agent. The game controller will call this with an updated game object
        every time the agent is expected to make a move.
        """
        board = game.get_board()
        opponent_token = game.player2_token() if game.player1_token() == self.token() else game.player1_token()

        # First priority: Try to win
        for move in self.get_possible_moves(board):
            if self.is_winning_move(board, move, self.token()):
                return move
        
        # Second priority: Block opponent from winning
        for move in self.get_possible_moves(board):
            if self.is_winning_move(board, move, opponent_token):
                return move
        
        # Third priority: Take the center if available
        if board[1, 1] == '':
            return (1, 1)
        
        # Fourth priority: Take any corner if available
        for move in [(0, 0), (0, 2), (2, 0), (2, 2)]:
            if board[move[0]][move[1]] == '':
                return move

        # Last resort: Pick the first available move
        for move in self.get_possible_moves(board):
            return move

        return None  # Should never reach here

    def get_possible_moves(self, board):
        return [(i, j) for i in range(3) for j in range(3) if board[i][j] == '']

    def is_winning_move(self, board, move, token):
        """
        Check if placing a token at the specified move will result in a win.
        """
        temp_board = np.copy(board)
        temp_board[move[0]][move[1]] = token.value()
        return self.is_winner(temp_board, token)

    def is_winner(self, board, token):
        """
        Check rows, columns, and two diagonals for winning condition.
        """
        lines = [
            board[0], board[1], board[2],  # Rows
            board[:,0], board[:,1], board[:,2],  # Columns
            [board[i][i] for i in range(3)],  # Main diagonal
            [board[i][2-i] for i in range(3)]  # Second diagonal
        ]
        return any(all(token.value() == cell for cell in line) for line in lines)
