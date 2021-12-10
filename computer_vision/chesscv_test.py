from chess_cv import ccv
import cv2
import game_flow.game as gfg

CV = ccv(square_width=17, board_size=7, cam_height=480, cam_width=640, fps=30, webcam=False, draw_info=False,
         input_video="../test_videos/480_Aruco_Board.mp4",
         chess_icons="../assets/chess_pieces.png")

# Initialize variables
param = [None]
key_press = None
window_name = 'C.H.E.S.S.'
cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, CV.click, param) # Create mouse click event

game = gfg.Game()

while CV.got_video:
    Mext = CV.next_frame()
    if Mext is not None:

        gameEnded, captured_piece = game.playGame()
        if captured_piece is not None:
            CV.captured_pieces.append(str(captured_piece))

        # Test the end game conditions to see if the game is over
        if gameEnded:   # Display GAME OVER message TODO reading accessibility
            cv2.putText(CV.bgr_display, text=game.outcomeString, org=(10, 40),
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=1.15, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(CV.bgr_display, text="Play Again? (y/n)", org=(10, CV.cam_height - 20),
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=1.15, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            # Overlay the same message in another color slightly offset to add readability on dark or light surfaces
            cv2.putText(CV.bgr_display, text=game.outcomeString, org=(12, 40),
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=1.15, color=(255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(CV.bgr_display, text="Play Again? (y/n)", org=(12, CV.cam_height - 20),
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=1.15, color=(255, 255, 255), thickness=2, lineType=cv2.LINE_AA)

            # Prompt the user if they would like to play again
            if key_press == ord('y'):
                game.resetBoard()
                CV.captured_pieces = []  # Empty out the set of captured pieces
            elif key_press == ord('n'):
                break
        else:   # If the game is not yet over:
            if param[-1] is not None:
                if game.players[game.currentPlayer] == game.Human:
                    if not game.Human.haveSelectedFromPiece:    # If the player has NOT chosen which piece to move:
                        game.Human.selectedSquare = param[-1]   # Get the users desired piece to move
                        game.Human.haveSelectedFromPiece = True
                    # If the user has selected a piece to move but NOT a place for it to go to:
                    elif (not game.Human.haveSelectedToPiece) and game.Human.haveDeterminedMoves:
                        game.Human.selectedSquare = param[-1]   # Get the users desired place to move their piece
                        game.Human.haveSelectedToPiece = True

                param.pop()  # Remove the most recent user input [mouse click event]

            else:
                pass    # If the chessboard cannot be found then don't change anything and wait until it can be seen

    # Display the updated chessboard. Only show the available moves if the current player is the human
    CV.show_image(window_name=window_name,
                  board_state=game.getGameState(),
                  my_moves=game.players[game.currentPlayer].my_moves if game.players[game.currentPlayer] == game.Human else None,
                  selected_piece=game.players[game.currentPlayer].fromPiece if game.players[game.currentPlayer] == game.Human else None,
                  Mext=Mext)
    key_press = cv2.waitKey(int(1000 / CV.fps))
    if key_press == 27:
        break
