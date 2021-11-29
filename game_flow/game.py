# C. H. E. S. S.
#game loop here

import chess
import game_flow.player as player
import numpy as np

class Game:
    def __init__(self):
        self.board = chess.Board()
        self.AI = player.AIPlayer(chess.WHITE)
        self.Human = player.HumanPlayer(chess.BLACK)
        self.players = [self.AI, self.Human]
        #need two players
        #need to set players colors
        #need to set and store which player will go first
        self.currentPlayer = 0
        self.outcomeString = None

    def playGame(self):
        # if (self.AI.isMyTurn):
        #     self.AI.doMove(self.board)
        # elif(self.Human.isMyTurn):
        #     self.Human.doMove(self.board)
        #print(self.currentPlayer)
        if not self.end_conditions():
            turn_completed, captured_piece = self.players[self.currentPlayer].doMove(self.board)
            if (turn_completed):
                self.currentPlayer = 1 - self.currentPlayer
        else:
            captured_piece = None
        return self.end_conditions(), captured_piece

    def getGameState(self):
        split_board = str(self.board).split('\n')
        final_board = np.array([row.split(' ') for row in split_board])
        return np.rot90(final_board, 2)

    def end_conditions(self):
        if self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_fivefold_repetition() or self.board.is_seventyfive_moves():
            #print("Game over")
            outcome = self.board.outcome(claim_draw=True)
            if outcome.winner:
                color = "White"
            else:
                color = "Black"
            if self.board.is_checkmate():
                self.outcomeString = "Checkmate - " + color + " Wins"
                #print("Game finished by checkmate")
            if self.board.is_stalemate():
                #print("Game finished by stalemate")
                self.outcomeString = "Stalemate"
            if self.board.is_fivefold_repetition():
                #print("Game finished by ifivefold repetition")
                self.outcomeString = "Stalemate - Five-Fold Repetition"
            if self.board.is_seventyfive_moves():
                #print("Game finished by seventyfive moves")
                self.outcomeString = "Stalemate - 75 Moves"

            return True
        return False

    def resetBoard(self):
        self.board = chess.Board()
        self.currentPlayer = 0
        self.outcomeString = None