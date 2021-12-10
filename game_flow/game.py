# C. H. E. S. S.
# game loop here

import chess
import game_flow.player as player
import numpy as np


class Game:

    # Initialize the game
    def __init__(self):
        self.board = chess.Board()
        self.AI = player.AIPlayer(chess.WHITE)
        self.Human = player.HumanPlayer(chess.BLACK)
        self.players = [self.AI, self.Human]
        self.currentPlayer = 0
        self.outcomeString = None

    def playGame(self):
        if not self.end_conditions():                   # If the game has not ended
            turn_completed, captured_piece = self.players[self.currentPlayer].doMove(self.board)  # Wait for next move
            if (turn_completed):
                self.currentPlayer = 1 - self.currentPlayer
        else:
            captured_piece = None
        return self.end_conditions(), captured_piece    # Return any updated information about the game for the board

    # Parse the game board returned by the python chess library
    def getGameState(self):
        split_board = str(self.board).split('\n')
        final_board = np.array([row.split(' ') for row in split_board])
        return np.rot90(final_board, 2)

    # Check if the game has ended according to different end game scenarios
    def end_conditions(self):
        if self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_fivefold_repetition() or self.board.is_seventyfive_moves():
            outcome = self.board.outcome(claim_draw=True)
            if outcome.winner:
                color = "White"
            else:
                color = "Black"
            if self.board.is_checkmate():
                self.outcomeString = "Checkmate - " + color + " Wins"
            if self.board.is_stalemate():
                self.outcomeString = "Stalemate"
            if self.board.is_fivefold_repetition():
                self.outcomeString = "Stalemate - Five-Fold Repetition"
            if self.board.is_seventyfive_moves():
                self.outcomeString = "Stalemate - 75 Moves"

            return True
        return False

    # Clears and resets the board to its initial state
    def resetBoard(self):
        self.board = chess.Board()
        self.currentPlayer = 0
        self.outcomeString = None
