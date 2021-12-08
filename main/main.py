from homography.ChessCV import CCV
import cv2
import game_flow.game as gfg

CV = CCV(square_width=17, board_size=7, cam_height=480, cam_width=640, fps=60, webcam=False, draw_info=False,
         input_video="../test_videos/480_Aruco_Still.mp4",
         chess_icons="../assets/chess_pieces.png",
         write_video=False, output_video="Demo.mp4")

param = [None]
key_press = None
window_name = 'C.H.E.S.S.'
cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, CV.click, param)

game = gfg.Game()

while CV.got_video:
    Mext = CV.next_frame()
    if Mext is not None:

        gameEnded, captured_piece = game.playGame()
        if captured_piece is not None:
            CV.captured_pieces.append(str(captured_piece))

        if (gameEnded):
            cv2.putText(CV.bgr_display, text=game.outcomeString, org=(10, 40),
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=1.15, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(CV.bgr_display, text="Play Again? (y/n)", org=(10, CV.cam_height - 20),
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=1.15, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(CV.bgr_display, text=game.outcomeString, org=(12, 40),
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=1.15, color=(255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(CV.bgr_display, text="Play Again? (y/n)", org=(12, CV.cam_height - 20),
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=1.15, color=(255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
            if key_press == ord('y'):
                game.resetBoard()
                CV.captured_pieces = []
            elif key_press == ord('n'):
                break
        else:
            # get user input
            if param[-1] is not None:
                if game.players[game.currentPlayer] == game.Human:
                    if not game.Human.haveSelectedFromPiece:
                        game.Human.selectedSquare = param[-1]
                        game.Human.haveSelectedFromPiece = True
                    elif (not game.Human.haveSelectedToPiece) and game.Human.haveDeterminedMoves:
                        game.Human.selectedSquare = param[-1]
                        game.Human.haveSelectedToPiece = True

                param.pop()

            else:
                pass

    CV.show_image(window_name=window_name,
                  board_state=game.getGameState(),
                  my_moves=game.players[game.currentPlayer].my_moves if game.players[game.currentPlayer] == game.Human else None)
    key_press = cv2.waitKey(int(1000 / CV.fps))
    if key_press == 27:
        break
if CV.write_video:
    CV.videoWriter.release()
