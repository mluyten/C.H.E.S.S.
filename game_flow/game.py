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

    def playGame(self):
        if (self.end_conditions()):
            return True
        # if (self.AI.isMyTurn):
        #     self.AI.doMove(self.board)
        # elif(self.Human.isMyTurn):
        #     self.Human.doMove(self.board)
        #print(self.currentPlayer)
        turn_completed = self.players[self.currentPlayer].doMove(self.board)
        if (turn_completed):
            self.currentPlayer = 1 - self.currentPlayer

    def getGameState(self):
        split_board = str(self.board).split('\n')
        final_board = np.array([row.split(' ') for row in split_board])
        return np.rot90(final_board, 2)

    def end_conditions(self):
        if self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_fivefold_repetition() or self.board.is_seventyfive_moves():
            print("Game over")
            if self.board.is_checkmate():
                print("Game finished by checkmate")
            if self.board.is_stalemate():
                print("Game finished by stalemate")
            if self.board.is_fivefold_repetition():
                print("Game finished by ifivefold repetition")
            if self.board.is_seventyfive_moves():
                print("Game finished by seventyfive moves")

            return True
        return False
