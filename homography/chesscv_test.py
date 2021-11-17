from ChessCV import CCV
import numpy as np
import cv2

CV = CCV(17, 7, 480, 640, 30, webcam=False, input_video="../test_videos/480_Aruco_Board.mp4")

param = [None]
cv2.namedWindow("vid")
cv2.setMouseCallback("vid", CV.click, param)

while CV.got_video:
    Mext = CV.next_frame()
    if Mext is not None:
        CV.draw_spaces_and_origin(Mext)
        if param[-1] is not None:
            cv2.putText(CV.bgr_display, text=param[-1], org=(10, 470),
                        # Displays name of clicked square at bottom right of screen
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=(255, 0, 255), thickness=2)
    else:
        CV.outer_corners = None
        cv2.putText(CV.bgr_display, text="Chessboard/ArUco Not Found", org=(10, 470),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1, color=(255, 0, 255), thickness=2)

    cv2.imshow("vid", CV.bgr_display)
    cv2.waitKey(int(1000 / CV.fps))

