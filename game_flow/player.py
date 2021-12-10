# C. H. E. S. S.
# player control

import chess
import random


# enum for turn state:
# not my turn
# is my trn
# have selected my piece

class Player:
    def __init__(self, color):
        self.color = color

    def doMove(self, board):
        pass


class AIPlayer(Player):

    # Pick a legal move at random and move the AI there
    def doMove(self, board):
        legal_moves = list(board.legal_moves)
        random_index = int(random.random() * len(legal_moves))
        move = str(legal_moves[random_index])
        if board.is_capture(legal_moves[random_index]):
            captured_piece = board.piece_at(chess.parse_square(move[2:4]))
        else:
            captured_piece = None
        print("AI move: ", move)
        board.push_san(move)
        return True, captured_piece

    # TODO display AI last move


class HumanPlayer(Player):

    # Initialize the human player
    def __init__(self, color):
        super().__init__(color)
        clear_move(self)
        self.selectedSquare = None

    def doMove(self, board):
        if (not self.haveSelectedFromPiece):    # Wait for the human to select a piece
            return False, None
        elif (not self.haveDeterminedMoves):    # Show the user the available moves from the selected piece
            self.fromPiece = chess.parse_square(self.selectedSquare)
            legal_moves = list(board.legal_moves)
            index = chess.parse_square(self.selectedSquare)
            for move in legal_moves:
                if move.from_square == index:
                    self.my_moves.append(move)  # Get the possible moves from the selected piece
            if (len(self.my_moves) == 0):
                print("invalid source square. please select a new one")
                self.haveSelectedFromPiece = False
                self.fromPiece = None
                return False, None
            self.haveDeterminedMoves = True
            return False, None
        elif (not self.haveSelectedToPiece):    # Wait for the user to select a place to move to
            return False, None
        else:                                   # Process the players selected move
            my_move = None
            index = chess.parse_square(self.selectedSquare)
            # Clear the data associated with the move if it is selected twice
            if index == self.fromPiece:
                clear_move(self)
                return False, None
            # Parse the most recent move from the list of moves
            for move in self.my_moves:
                if move.to_square == index:
                    my_move = move
                    break
            if my_move == None:
                print("invalid destination square. please select a new one")
                self.haveSelectedToPiece = False
                return False, None
            # Update the side panels to show the new captured piece
            if board.is_capture(move):
                captured_piece = str(board.piece_at(chess.parse_square(str(move)[2:4])))
            else:
                captured_piece = None
            move = str(move)

            print("Player move: ", move)
            board.push_san(move)
            clear_move(self)
            return True, captured_piece
        return False, None

# Clear the human moves
def clear_move(self):
    self.haveSelectedFromPiece = False
    self.haveDeterminedMoves = False
    self.haveSelectedToPiece = False
    self.my_moves = []
    self.fromPiece = None

