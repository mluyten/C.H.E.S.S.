import chess
import random


def play_game():
    board = chess.Board()  # create board object
    is_AI_turn = False
    print("Start game")
    while not end_conditions(board):
        if is_AI_turn:
            print("AI turn")
            all_moves = list(board.legal_moves)
            random_index = int(random.random() * len(all_moves))
            move = str(all_moves[random_index])  # get a random legal move
            print(move)
            board.push_san(str(move))  # move AI piece
            is_AI_turn = False

        else:
            print("Player turn")
            move = str(list(board.legal_moves)[0])  # get the first legal move
            # print(board.legal_moves)  # legal moves
            # print(list(board.legal_moves)[0])
            # move = input("Desired move:")
            print("moving", move)
            try:
                board.push_san(move)  # Move your piece
            except:
                print("Invalid move. Choose again")
            is_AI_turn = True

        print(board, "\n")  # display chess board


# board.is_checkmate()  # Verifying check mate. Returns boolean TRUE or FALSE
# # Stalemate is a situation in the game of chess where the player whose turn it is to move is not in check but has
# # no legal move. The rules of chess provide that when stalemate occurs, the game ends as a draw.
# board.is_stalemate()  # Verifying stalemate. Returns boolean TRUE or FALSE
# board.is_check()
# # A game ends as a draw (even without a claim) once a fivefold repetition occurs or if there are 75 moves without a
# # pawn push or capture. Other ways of ending a game take precedence
# board.is_fivefold_repetition()
# board.is_seventyfive_moves()
def end_conditions(board):
    if board.is_checkmate() or board.is_stalemate() or board.is_fivefold_repetition() or board.is_seventyfive_moves():
        print("Game over")
        if board.is_checkmate():
            print("Game finished by checkmate")
        if board.is_stalemate():
            print("Game finished by stalemate")
        if board.is_fivefold_repetition():
            print("Game finished by ifivefold repetition")
        if board.is_seventyfive_moves():
            print("Game finished by seventyfive moves")

        return True
    return False


def main():
    play_game()


if __name__ == '__main__':
    main()
