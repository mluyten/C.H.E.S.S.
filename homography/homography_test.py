# C.H.E.S.S

import sys
import cv2
import numpy as np

WEBCAM = False
CAM_NUM = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
FPS = 30
BOARD_SIZE = 7
SQUARE_WIDTH = 17
WRITE_VIDEO = False

CORNERS_WORLD = np.array([[SQUARE_WIDTH, SQUARE_WIDTH, 0],
                 [SQUARE_WIDTH, BOARD_SIZE * SQUARE_WIDTH, 0],
                 [BOARD_SIZE * SQUARE_WIDTH, SQUARE_WIDTH, 0],
                 [BOARD_SIZE * SQUARE_WIDTH, BOARD_SIZE * SQUARE_WIDTH, 0]], dtype=np.float32)

CORNERS_AFFINE = np.array([[100, 100],
                 [100 * BOARD_SIZE, 100],
                 [100, 100 * BOARD_SIZE],
                 [100 * BOARD_SIZE, 100 * BOARD_SIZE]], dtype=np.float32)

SQUARES = np.chararray((BOARD_SIZE + 1, BOARD_SIZE + 1, 2), itemsize=2)

STARTING_PIECES = {
    "r": ["A1", "H1"],
    "n": ["B1", "G1"],
    "b": ["C1", "F1"],
    "q": ["D1"],
    "k": ["E1"],
    "p": ["A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2"],
    "R": ["A8", "H8"],
    "N": ["B8", "G8"],
    "B": ["C8", "F8"],
    "Q": ["D8"],
    "K": ["E8"],
    "P": ["A7", "B7", "C7", "D7", "E7", "F7", "G7", "H7"],
}

outerCorners = None
bgr_image = None

def findPoseAndDrawOrigin(pts, K, bgr_image):
    PoseFound, rvec, tvec = cv2.solvePnP(objectPoints=CORNERS_WORLD, imagePoints=pts, cameraMatrix=K, distCoeffs=None) # Finds r and t vectors for homography
    if PoseFound: # Draws origin coordinate axis
        W = np.amax(CORNERS_WORLD, axis=0) - np.amin(CORNERS_WORLD, axis=0)
        L = np.linalg.norm(W)
        d = L / 5
        pAxes = np.float32([[0, 0, 0], [d, 0, 0], [0, d, 0], [0, 0, d]])
        pImg, J = cv2.projectPoints(objectPoints=pAxes, rvec=rvec, tvec=tvec, cameraMatrix=K, distCoeffs=None)
        pImg = pImg.reshape(-1, 2)
        cv2.line(bgr_image, tuple(np.int32(pImg[0])), tuple(np.int32(pImg[1])), (0, 0, 255), 2, lineType=cv2.LINE_AA)
        cv2.line(bgr_image, tuple(np.int32(pImg[0])), tuple(np.int32(pImg[2])), (0, 255, 0), 2, lineType=cv2.LINE_AA)
        cv2.line(bgr_image, tuple(np.int32(pImg[0])), tuple(np.int32(pImg[3])), (255, 0, 0), 2, lineType=cv2.LINE_AA)
        return True, rvec, tvec
    else:
        return False, None, None

# https://www.geeksforgeeks.org/python-find-closest-number-to-k-in-given-list/#:~:text=Given%20a%20list%20of%20numbers%20and%20a%20variable,K%2C%20and%20returns%20the%20element%20having%20minimum%20difference.
def closest(lst, K):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]


def orderPoints(corners, aruco_location):
    aruco_center = np.array([np.average(aruco_location[0, :, 0]), np.average(aruco_location[0, :, 1])])

    corners_reshape = corners.reshape((49, 2)) # reshape to 40x2 array
    corner_dist = [np.sqrt((corner[0] - aruco_center[0])**2 + (corner[1] - aruco_center[1])**2) for corner in corners_reshape]

    closest_val = closest([0, 6, 42, 48], np.argmin(corner_dist))
    if closest_val == 6:
        corners_reshape = corners.reshape((7, 7, 2))
        corners_reshape = np.rot90(corners_reshape, 1, axes=(0, 1))
    elif closest_val == 42:
        corners_reshape = corners.reshape((7, 7, 2))
        corners_reshape = np.rot90(corners_reshape, 3, axes=(0, 1))
    elif closest_val == 48:
        corners_reshape = corners.reshape((7, 7, 2))
        corners_reshape = np.rot90(corners_reshape, 2, axes=(0, 1))

    return corners_reshape.reshape((49, 1, 2))

# Generates a 2D array of board spaces A1-H8
def genSpaces():
    for i in range(BOARD_SIZE + 1):
        for j in range(BOARD_SIZE + 1):
            SQUARES[i][j][0] = str(chr(65 + j)) + str(i + 1)
            SQUARES[i][j][1] = setBoard(str(chr(65 + j)) + str(i + 1))

# Adds the starting positions of each piece on the board
def setBoard(position):
    for piece in STARTING_PIECES:
        for square in STARTING_PIECES[piece]:
            if str(position) == square:
                return piece
    return ""

# Draws the name of each square on the board
def drawPositions(bgr_image, K, Mext):
    for i in range(BOARD_SIZE + 1):
        for j in range(BOARD_SIZE + 1):
            pos = np.array([SQUARE_WIDTH / 2 + i * SQUARE_WIDTH, SQUARE_WIDTH / 2 + j * SQUARE_WIDTH, 0], dtype=np.float32)
            p = K @ Mext @ (np.block([pos, 1]).T)
            point = (int(p[0] / p[2]), int(p[1] / p[2]))
            cv2.putText(bgr_image, text=str(SQUARES[i][j][0].decode("utf-8")), org=point,
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5, color=(0, 0, 255), thickness=2)
            cv2.drawMarker(bgr_image, position=point, color=(0, 0, 255), markerType=cv2.MARKER_CROSS)

# Finds the homography of the board
def findBoardHomography(bgr_image, K):
    global outerCorners
    arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    arucoCorners, ids, _ = cv2.aruco.detectMarkers(
        image=bgr_image,
        dictionary=arucoDict
    )
    ret_val, corners = cv2.findChessboardCorners(image=bgr_image, patternSize=(BOARD_SIZE, BOARD_SIZE))

    if ret_val and ids is not None:
        ret_val, corners = cv2.findChessboardCorners(image=bgr_image, patternSize=(BOARD_SIZE, BOARD_SIZE))
        corners = orderPoints(corners, arucoCorners[0])
        outerCorners = np.array([[corners[0][0][0], corners[0][0][1]],  # Finds the outer corners of the findChessBoardCorners points
             [corners[BOARD_SIZE - 1][0][0], corners[BOARD_SIZE - 1][0][1]],
             [corners[BOARD_SIZE ** 2 - BOARD_SIZE][0][0], corners[BOARD_SIZE ** 2 - BOARD_SIZE][0][1]],
             [corners[BOARD_SIZE ** 2 - 1][0][0], corners[BOARD_SIZE ** 2 - 1][0][1]]], dtype=np.float32)

        gotPose, rvec, tvec = findPoseAndDrawOrigin(outerCorners, K, bgr_image)  # Find homography and draw
        if gotPose:
            R = cv2.Rodrigues(rvec)
            return True, np.block([[R[0], tvec], [0, 0, 0, 1]])
        else:
            return False, None
    else:
        return False, None

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

    genSpaces()
    global outerCorners

    if WEBCAM:
        video_capture = cv2.VideoCapture(CAM_NUM)  # Open video capture object
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)  # set cam width
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)  # set cam height
    else:
        video_capture = cv2.VideoCapture("../test_videos/480_Aruco_Board.mp4")  # Open video capture object

    is_ok, bgr_image_input = video_capture.read()  # Make sure we can read video
    if not is_ok:
        print("Cannot read video source")
        sys.exit()

    param = [None]
    got_vid, bgr_image = video_capture.read()
    cv2.namedWindow("vid")
    cv2.setMouseCallback("vid", click, param)

    if WRITE_VIDEO:
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        videoWriter = cv2.VideoWriter("output.mp4", fourcc=fourcc, fps=30.0,
                                      frameSize=(CAM_WIDTH, CAM_HEIGHT))

    print("Hit ESC to quit...")

    while True:
        got_vid, bgr_image = video_capture.read()
        if not got_vid:
            break  # no camera, or reached end of video file
        bgr_display = bgr_image.copy()
        gotHomography, H = findBoardHomography(bgr_display, K)  # Returns homography from camera to world coordinates if chess board and aruco marker are detected
        if gotHomography:
            Mext = H[0:3][:]
            drawPositions(bgr_display, K, Mext)
            if param[-1] != None:
                cv2.putText(bgr_display, text=param[-1], org=(10, 470),  # Displays name of clicked square at bottom right of screen
                           fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                           fontScale=1, color=(255, 0, 255), thickness=2)

        else:
            outerCorners = None
            cv2.putText(bgr_display, text="Chessboard/ArUco Not Found", org=(10, 470),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=(255, 0, 255), thickness=2)

        cv2.imshow("vid", bgr_display)
        key_pressed = cv2.waitKey(int(1000 / FPS))
        if key_pressed == 27:
            break

        if WRITE_VIDEO:
            videoWriter.write(bgr_image)

    if WRITE_VIDEO:
        videoWriter.release()

    video_capture.release()
    cv2.destroyAllWindows()

def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global outerCorners
        global bgr_image
        if outerCorners.any() != None:
            H, _ = cv2.findHomography(outerCorners, CORNERS_AFFINE)  # Finds orthophoto homography
            point = H @ [x, y, 1]  # Calculates position of mouse click point on orthophoto
            point[0] = point[0] / point[2]
            point[1] = point[1] / point[2]

            if point[0] < ((BOARD_SIZE + 1) * 100) and point[0] > 0 and point[1] < ((BOARD_SIZE + 1) * 100) and point[1] > 0:
                param.append(str(SQUARES[int(point[1]/100)][int(point[0]/100)][0].decode("utf-8")))
            else:
                param.append("Not on Board")

if __name__ == '__main__':
    main()