# C.H.E.S.S

import sys
import cv2
import numpy as np

CAM_NUM = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
FPS = 30
BOARD_SIZE = 7
SQUARE_WIDTH = 17

CORNERS_WORLD = np.array([[SQUARE_WIDTH, SQUARE_WIDTH, 0],
                 [SQUARE_WIDTH, BOARD_SIZE * SQUARE_WIDTH, 0],
                 [BOARD_SIZE * SQUARE_WIDTH, SQUARE_WIDTH, 0],
                 [BOARD_SIZE * SQUARE_WIDTH, BOARD_SIZE * SQUARE_WIDTH, 0]], dtype=np.float32)

points = np.array([[SQUARE_WIDTH / 2, SQUARE_WIDTH / 2, 0],
                    [SQUARE_WIDTH * BOARD_SIZE + (SQUARE_WIDTH / 2),
                    SQUARE_WIDTH * BOARD_SIZE + (SQUARE_WIDTH / 2), 0]], dtype=np.float32)

squares = ["A1", "H8"]

def findPoseAndDrawOrigin(pts, K, bgr_image):
    PoseFound, rvec, tvec = cv2.solvePnP(objectPoints=CORNERS_WORLD, imagePoints=pts, cameraMatrix=K, distCoeffs=None) # Finds r and t vectors for homography
    if PoseFound: # Draws origin coordinate axis
        W = np.amax(CORNERS_WORLD, axis=0) - np.amin(CORNERS_WORLD, axis=0)
        L = np.linalg.norm(W)
        d = L / 5
        pAxes = np.float32([[0, 0, 0], [d, 0, 0], [0, d, 0], [0, 0, d]])
        pImg, J = cv2.projectPoints(objectPoints=pAxes, rvec=rvec, tvec=tvec, cameraMatrix=K, distCoeffs=None)
        pImg = pImg.reshape(-1, 2)
        cv2.line(bgr_image, tuple(np.int32(pImg[0])), tuple(np.int32(pImg[1])), (0, 0, 255), 2)
        cv2.line(bgr_image, tuple(np.int32(pImg[0])), tuple(np.int32(pImg[2])), (0, 255, 0), 2)
        cv2.line(bgr_image, tuple(np.int32(pImg[0])), tuple(np.int32(pImg[3])), (255, 0, 0), 2)
        return True, rvec, tvec
    else:
        return False, None, None

def main():
    # read in camera matrix and distortion coefficients
    cam_mat_file = open('../camera_calibration/camera_matrix.csv', 'rb')
    dist_coeff_file = open('../camera_calibration/dist_coeff.csv', 'rb')
    # read matrices from file
    K = np.loadtxt(cam_mat_file, delimiter=',')
    dist_coeffs = np.loadtxt(dist_coeff_file, delimiter=',')
    # close files
    cam_mat_file.close()
    dist_coeff_file.close()

    video_capture = cv2.VideoCapture("../test_videos/chess_1080.mp4")  # Open video capture object

    is_ok, bgr_image_input = video_capture.read()  # Make sure we can read video
    if not is_ok:
        print("Cannot read video source")
        sys.exit()

    fourcc = cv2.VideoWriter_fourcc('W', 'M', 'V', '2')
    videoWriter = cv2.VideoWriter("output.wmv", fourcc=fourcc, fps=30.0,
                                  frameSize=(CAM_WIDTH, CAM_HEIGHT))

    print("Hit ESC to quit...")

    while True:
        got_vid, bgr_image = video_capture.read()
        if not got_vid:
            break  # no camera, or reached end of video file

        # Find the chess board corners.
        ret_val, corners = cv2.findChessboardCorners(image=bgr_image, patternSize=(BOARD_SIZE, BOARD_SIZE))

        outer_corners = np.array([[corners[0][0][0], corners[0][0][1]],  # Finds the outer corners of the findChessBoardCorners points
                         [corners[BOARD_SIZE - 1][0][0], corners[BOARD_SIZE - 1][0][1]],
                         [corners[BOARD_SIZE ** 2 - BOARD_SIZE][0][0], corners[BOARD_SIZE ** 2 - BOARD_SIZE][0][1]],
                         [corners[BOARD_SIZE ** 2 - 1][0][0], corners[BOARD_SIZE ** 2 - 1][0][1]]], dtype=np.float32)

        bgr_display = bgr_image.copy()
        gotPose, rvec, tvec = findPoseAndDrawOrigin(outer_corners, K, bgr_display) # Find homography and draw
        if gotPose:
            R = cv2.Rodrigues(rvec)
            H = np.block([[R[0], tvec], [0, 0, 0, 1]])
            Mext = H[0:3][:]
            for i in range(len(squares)):
                p = K @ Mext @ (np.block([points[i], 1]).T)
                point = (int(p[0] / p[2]), int(p[1] / p[2]))
                cv2.putText(bgr_display, text=squares[i], org=point,
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.5, color=(0, 0,255), thickness=2)
                cv2.drawMarker(bgr_display, position=point, color=(0, 0, 255), markerType=cv2.MARKER_CROSS)

        cv2.imshow("vid", bgr_display)
        key_pressed = cv2.waitKey(int(1000 / FPS))
        if key_pressed == 27:
            break
        videoWriter.write(bgr_image)
    videoWriter.release()
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
