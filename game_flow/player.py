# C. H. E. S. S.
#player control

#enum for turn state:
    #not my turn
    #is my trn
    #have selected my piece

class Player:
    def __init__(self, color):
        self.color = color
        self.isMyTurn = False

    def doMove(self, board):
        pass

class AIPlayer(Player):

    def doMove(self, board):
        pass

class HumanPlayer(Player):

    def __init__(self, color):
        super().__init__(self, color)
        #self.isMyTurn = False
        self.haveSelectedPiece = False
        self.moveIsCompleted = False

    def doMove(self, board):
        pass