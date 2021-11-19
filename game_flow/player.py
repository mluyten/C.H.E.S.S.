# C. H. E. S. S.
#player control

import chess
import random

#enum for turn state:
    #not my turn
    #is my trn
    #have selected my piece

class Player:
    def __init__(self, color):
        self.color = color

    def doMove(self, board):
        pass

class AIPlayer(Player):

    def doMove(self, board):
        # print("ai do move")
        legal_moves = list(board.legal_moves)
        random_index = int(random.random() * len(legal_moves))
        move = str(legal_moves[random_index])
        board.push_san(move)
        return True


class HumanPlayer(Player):

    def __init__(self, color):
        super().__init__(color)
        #self.isMyTurn = False
        #self.isMyTurn = False
        self.haveSelectedFromPiece = False
        self.haveDeterminedMoves = False
        self.haveSelectedToPiece = False
        self.selectedSquare = None
        self.my_moves = []

    def doMove(self, board):
        # print("human do move")
        if ( not self.haveSelectedFromPiece):
            return False
        elif ( not self.haveDeterminedMoves):
            legal_moves = list(board.legal_moves)
            index = chess.parse_square(self.selectedSquare)
            for move in legal_moves:
                if move.from_square == index:
                    self.my_moves.append(move)
            print(self.my_moves)
            if (len(self.my_moves) == 0):
                print("invalid source square. please select a new one")
                self.haveSelectedFromPiece = False
                return False
            self.haveDeterminedMoves = True
            return False
        elif (not self.haveSelectedToPiece):
            return False
        else:
            my_move = None
            index = chess.parse_square(self.selectedSquare)
            for move in self.my_moves:
                if move.to_square == index:
                    my_move = move
                    break
            if my_move == None:
                print("invalid destination square. please select a new one")
                self.haveSelectedToPiece = False
                return False
            move = str(move)
            print("player move: ", move)
            board.push_san(move)
            #get san
            #push to board
            #reset move state
            self.haveSelectedFromPiece = False
            self.haveDeterminedMoves = False
            self.haveSelectedToPiece = False
            self.my_moves = []
            return True

        #random_index = int(random.random() * len(legal_moves))
        #move = str(legal_moves[random_index])
        #board.push_san(move)
        #self.isMyTurn = False
        return False