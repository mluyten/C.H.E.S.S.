# C. H. E. S. S.
#game loop here

import chess
import player

class Game:
    def __init__(self):
        self.board = chess.Board()
        self.AI = player.AIPlayer(chess.WHITE)
        self.Human = player.HumanPlayer(chess.BLACK)
        #need two players
        #need to set players colors
        #need to set and store which player will go first
        self.AI.isMyTurn = True

    def playGame(self):
        if (self.end_conditions()):
            #todo: go to game end here
            return
        if (self.AI.isMyTurn):
            self.AI.doMove(self.board)
        elif(self.Human.isMyTurn):
            self.Human.doMove(self.board)

    def getGameState(self):
        # Caleb: feel free to edit this! this is intended to get you what you need of the game state
        return self.board

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
