from Game import Game, Type
from Token import Token
import numpy as np
import Connect4Game
import TicTacToeGame

class GameAgent:
    def __init__(self, token: Token):
        self._token = token
        self.INF = 100000
        self.transposition_table = {}
        self.col_weights = None

    def token(self) -> Token:
        return self._token

    def make_move(self, game: Game):
        if game.get_type() == Type.TIC_TAC_TOE:
            return self._make_tictactoe_move(game)
        else:
            return self._make_connect4_move(game)

    def _make_tictactoe_move(self, game: Game):
        board = game.get_board()
        my_token = self._token
        opp_token = game.player1_token() if game.player1_token() != my_token else game.player2_token()
        best_val = -self.INF
        best_move = (-1, -1)
        for r in range(3):
            for c in range(3):
                if TicTacToeGame.is_valid_position(board, r, c):
                    board[r][c] = my_token.value()
                    move_val = self._ttt_minimax(board, False, my_token, opp_token)
                    board[r][c] = ''
                    if move_val > best_val:
                        best_val = move_val
                        best_move = (r, c)
        return best_move

    def _ttt_minimax(self, board, is_my_turn, my_token, opp_token):
        if TicTacToeGame.winning_move(board, my_token):
            return 10
        if TicTacToeGame.winning_move(board, opp_token):
            return -10
        if self._ttt_board_full(board):
            return 0
        if is_my_turn:
            best = -self.INF
            for r in range(3):
                for c in range(3):
                    if TicTacToeGame.is_valid_position(board, r, c):
                        board[r][c] = my_token.value()
                        val = self._ttt_minimax(board, False, my_token, opp_token)
                        board[r][c] = ''
                        if val > best:
                            best = val
            return best
        else:
            best = self.INF
            for r in range(3):
                for c in range(3):
                    if TicTacToeGame.is_valid_position(board, r, c):
                        board[r][c] = opp_token.value()
                        val = self._ttt_minimax(board, True, my_token, opp_token)
                        board[r][c] = ''
                        if val < best:
                            best = val
            return best

    def _ttt_board_full(self, board):
        return np.count_nonzero(board) == 9

    def _make_connect4_move(self, game: Game):
        board = game.get_board()
        seq = game.number_of_seq_tokens_needed()
        my_token = self._token
        player_tokens = [t for t in [game.player1_token(), game.player2_token(), game.player3_token()] if t is not None]
        opponents = [t for t in player_tokens if t != my_token]
        num_players = len(player_tokens)
        max_depth = 6 if num_players == 2 else 4
        self.max_depth_connect4 = max_depth
        valid_moves = [c for c in range(game.get_column_count()) if Connect4Game.column_has_space(board, c)]
        if self.col_weights is None:
            cols = game.get_column_count()
            mid = (cols - 1) / 2.0
            self.col_weights = [(cols - abs(c - mid)) for c in range(cols)]
        for col in valid_moves:
            temp_board = board.copy()
            Connect4Game.drop_piece(temp_board, col, my_token)
            if Connect4Game.is_winning_move(temp_board, my_token, seq):
                return col
        for col in valid_moves:
            for opp in opponents:
                temp_board = board.copy()
                Connect4Game.drop_piece(temp_board, col, opp)
                if Connect4Game.is_winning_move(temp_board, opp, seq):
                    return col
        current_index = player_tokens.index(my_token)
        move_scores = []
        for col in valid_moves:
            temp_board = board.copy()
            Connect4Game.drop_piece(temp_board, col, my_token)
            h_score = self._evaluate_connect4_board(temp_board, player_tokens, seq) + self.col_weights[col]*2
            move_scores.append((h_score, col))
        move_scores.sort(key=lambda x: x[0], reverse=True)
        alpha = -self.INF
        beta = self.INF
        best_score = -self.INF
        best_col = -1
        for _, col in move_scores:
            temp_board = board.copy()
            Connect4Game.drop_piece(temp_board, col, my_token)
            score = self._connect4_minimax(game, temp_board, self._next_player_index(current_index, num_players),
                                           player_tokens, 1, alpha, beta)
            if score > best_score:
                best_score = score
                best_col = col
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        if best_col == -1:
            return -1
        return best_col

    def _next_player_index(self, current_index, num_players):
        return (current_index + 1) % num_players

    def _board_key(self, board, current_index, depth):
        return (board.tobytes(), current_index, depth)

    def _connect4_minimax(self, game: Game, board: np.ndarray, current_index: int, player_tokens: list,
                          depth: int, alpha: int, beta: int):
        seq = game.number_of_seq_tokens_needed()
        max_depth = self.max_depth_connect4
        current_player = player_tokens[current_index]
        key = self._board_key(board, current_index, depth)
        if key in self.transposition_table:
            return self.transposition_table[key]
        if Connect4Game.board_is_full(board) or depth >= max_depth:
            val = self._evaluate_connect4_board(board, player_tokens, seq)
            self.transposition_table[key] = val
            return val
        for p in player_tokens:
            if Connect4Game.is_winning_move(board, p, seq):
                if p == self._token:
                    val = 10000 - depth
                else:
                    val = -10000 + depth
                self.transposition_table[key] = val
                return val
        valid_moves = [c for c in range(board.shape[1]) if Connect4Game.column_has_space(board, c)]
        if not valid_moves:
            self.transposition_table[key] = 0
            return 0
        move_scores = []
        for col in valid_moves:
            temp_board = board.copy()
            Connect4Game.drop_piece(temp_board, col, current_player)
            h_score = self._evaluate_connect4_board(temp_board, player_tokens, seq) + self.col_weights[col]
            move_scores.append((h_score, col))
        move_scores.sort(key=lambda x: x[0], reverse=True)
        best_score = -self.INF
        for _, col in move_scores:
            temp_board = board.copy()
            Connect4Game.drop_piece(temp_board, col, current_player)
            score = self._connect4_minimax(game, temp_board, self._next_player_index(current_index, len(player_tokens)),
                                           player_tokens, depth+1, alpha, beta)
            if score > best_score:
                best_score = score
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        self.transposition_table[key] = best_score
        return best_score

    def _evaluate_connect4_board(self, board: np.ndarray, player_tokens: list, seq: int):
        my_score = self._count_connect4_potential(board, self._token, seq)
        opponents = [t for t in player_tokens if t != self._token]
        opp_score_sum = 0
        for opp in opponents:
            opp_score_sum += self._count_connect4_potential(board, opp, seq)
        return my_score - opp_score_sum

    def _count_connect4_potential(self, board: np.ndarray, token: Token, seq: int):
        rows = board.shape[0]
        cols = board.shape[1]
        val = token.value()
        score = 0
        def eval_line(cells):
            res = 0
            count = 0
            for cell in cells:
                if cell == val:
                    count += 1
                else:
                    if 2 <= count < seq:
                        res += (2 if count == 2 else 5 if count == 3 else 20 if count>=4 else 0)
                    count = 0
            if 2 <= count < seq:
                res += (2 if count == 2 else 5 if count == 3 else 20 if count>=4 else 0)
            return res
        for r in range(rows):
            line = board[r, :]
            base_score = eval_line(line)
            col_bonus = 0
            for c in range(cols):
                if line[c] == val:
                    col_bonus += self.col_weights[c]*0.1
            score += base_score + col_bonus
        for c in range(cols):
            line = board[:, c]
            base_score = eval_line(line)
            col_bonus = 0
            for rr in range(rows):
                if line[rr] == val:
                    col_bonus += self.col_weights[c]*0.1
            score += base_score + col_bonus
        for start_col in range(cols):
            diag_line = []
            diag_rpos = []
            diag_cpos = []
            r, cc = 0, start_col
            while r < rows and cc < cols:
                diag_line.append(board[r, cc])
                diag_rpos.append(r)
                diag_cpos.append(cc)
                r += 1
                cc += 1
            if len(diag_line) > 1:
                base_score = eval_line(diag_line)
                col_bonus = 0
                for rr, ccc in zip(diag_rpos, diag_cpos):
                    if board[rr, ccc] == val:
                        col_bonus += self.col_weights[ccc]*0.1
                score += base_score + col_bonus
        for start_row in range(1, rows):
            diag_line = []
            diag_rpos = []
            diag_cpos = []
            r, cc = start_row, 0
            while r < rows and cc < cols:
                diag_line.append(board[r, cc])
                diag_rpos.append(r)
                diag_cpos.append(cc)
                r += 1
                cc += 1
            if len(diag_line) > 1:
                base_score = eval_line(diag_line)
                col_bonus = 0
                for rr, ccc in zip(diag_rpos, diag_cpos):
                    if board[rr, ccc] == val:
                        col_bonus += self.col_weights[ccc]*0.1
                score += base_score + col_bonus
        for start_col in range(cols):
            diag_line = []
            diag_rpos = []
            diag_cpos = []
            r, cc = 0, start_col
            while r < rows and cc >= 0:
                diag_line.append(board[r, cc])
                diag_rpos.append(r)
                diag_cpos.append(cc)
                r += 1
                cc -= 1
            if len(diag_line) > 1:
                base_score = eval_line(diag_line)
                col_bonus = 0
                for rr, ccc in zip(diag_rpos, diag_cpos):
                    if board[rr, ccc] == val:
                        col_bonus += self.col_weights[ccc]*0.1
                score += base_score + col_bonus
        for start_row in range(1, rows):
            diag_line = []
            diag_rpos = []
            diag_cpos = []
            r, cc = start_row, cols - 1
            while r < rows and cc >= 0:
                diag_line.append(board[r, cc])
                diag_rpos.append(r)
                diag_cpos.append(cc)
                r += 1
                cc -= 1
            if len(diag_line) > 1:
                base_score = eval_line(diag_line)
                col_bonus = 0
                for rr, ccc in zip(diag_rpos, diag_cpos):
                    if board[rr, ccc] == val:
                        col_bonus += self.col_weights[ccc]*0.1
                score += base_score + col_bonus
        return score
