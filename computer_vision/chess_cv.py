import chess
import cv2
import numpy as np
import sys


class ccv:
    def __init__(self, square_width, board_size, cam_height, cam_width, fps,
                 webcam=True, cam_number=0, input_video=None, write_video=False, output_video=None, chess_icons=None,
                 draw_info=False,
                 cam_mat='../camera_calibration/camera_matrix.csv', dist_coeff='../camera_calibration/dist_coeff.csv',
                 select_color=(255, 0, 255, 100), attack_color=(0, 0, 255, 100), move_color=(51, 255, 255, 100)):
        # read in camera matrix and distortion coefficients
        self.got_video = None
        cam_mat_file = open(cam_mat, 'rb')
        dist_coeff_file = open(dist_coeff, 'rb')
        # read matrices from file
        self.K = np.loadtxt(cam_mat_file, delimiter=',')
        self.dist_coeffs = np.loadtxt(dist_coeff_file, delimiter=',')
        # close files
        cam_mat_file.close()
        dist_coeff_file.close()
        self.fps = fps

        # read in and process chess icons
        self.icons = self.readIcons(chess_icons)

        # store debug parameter
        self.draw_info = draw_info

        # stores board parameters
        self.square_width = square_width
        self.board_size = board_size
        # stores the corners of the board in world coordinates
        self.corners_world = np.array([[square_width, square_width, 0],
                                       [square_width, board_size * square_width, 0],
                                       [board_size * square_width, square_width, 0],
                                       [board_size * square_width, board_size * square_width, 0]], dtype=np.float32)
        # stores the corners of the board in a (board_size + 1) * 100 x (board_size + 1) * 100 orthophoto
        self.corners_ortho = np.array([[100, 100],
                                       [100 * board_size, 100],
                                       [100, 100 * board_size],
                                       [100 * board_size, 100 * board_size]], dtype=np.float32)
        self.outer_corners = None
        # creates and populates an array of labels for the squares on the chess board
        self.squares = np.chararray((board_size + 1, board_size + 1, 2), itemsize=2)
        self.gen_spaces()

        # stores camera parameters
        self.cam_height = cam_height
        self.cam_width = cam_width
        # creates video writer if write_video flag is True
        self.write_video = write_video
        if write_video:
            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            self.videoWriter = cv2.VideoWriter(output_video, fourcc=fourcc, fps=self.fps, frameSize=(cam_width, cam_height))
        # streams video from webcam if webcam flag is true - else, streams video from local video file
        if webcam:
            self.video_capture = cv2.VideoCapture(cam_number)  # Open video capture object
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)  # set cam width
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)  # set cam height
        else:
            self.video_capture = cv2.VideoCapture(input_video)  # Open video capture object

        # stores bgr images and attempts to pull a frame from video_capture device
        self.bgr_image = None
        self.bgr_display = None
        self.target_display = None
        self.next_frame()
        if not self.got_video:
            print("Cannot read video source")

        self.material_dim = 20
        start = int((self.cam_height - 16 * self.material_dim) / 2)
        self.material_bar = [[(10, start), (30, self.cam_height - start)],
                             [(self.cam_width - 10 - self.material_dim, start),
                              (self.cam_width - 10, self.cam_height - start)]]
        self.captured_pieces = []

        self.icon_dict = {
            'K': [0, 0],
            'k': [1, 0],
            'Q': [0, 1],
            'q': [1, 1],
            'B': [0, 2],
            'b': [1, 2],
            'N': [0, 3],
            'n': [1, 3],
            'R': [0, 4],
            'r': [1, 4],
            'P': [0, 5],
            'p': [1, 5]}

        self.select_color = select_color
        self.attack_color = attack_color
        self.move_color = move_color

    def readIcons(self, chess_icons):
        # read icons in the order: K, Q, B, N, R, P
        icon_map = cv2.imread(chess_icons, cv2.IMREAD_UNCHANGED)
        white_pieces = []
        black_pieces = []

        for i in range(0, 600, 100):
            white_piece = icon_map[0:100, i:i + 100, :]
            black_piece = icon_map[100:200, i:i + 100, :]
            white_pieces.append(white_piece)
            black_pieces.append(black_piece)

        white_pieces = np.array(white_pieces)
        black_pieces = np.array(black_pieces)

        return [white_pieces, black_pieces]

    def next_frame(self):  # pulls frames from
        if self.bgr_display is not None:
            if self.write_video:
                self.videoWriter.write(self.bgr_display[:,:,:3])

        self.got_video, self.bgr_image = self.video_capture.read()
        self.bgr_display = np.copy(self.bgr_image)

        if not self.got_video:
            return None
        else:
            # Returns homography from camera to world coordinates if chess board and aruco marker are detected
            gotHomography, H = self.find_board_homography()
            if gotHomography:
                return H[0:3][:]
            else:
                return None

    def find_pose(self, pts):
        pose_found, rvec, tvec = cv2.solvePnP(objectPoints=self.corners_world, imagePoints=pts, cameraMatrix=self.K,
                                              distCoeffs=None)  # Finds r and t vectors for homography

        if pose_found:
            return True, rvec, tvec
        else:
            return False, None, None

    def find_board_homography(self):
        global outerCorners
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        aruco_corners, ids, _ = cv2.aruco.detectMarkers(
            image=self.bgr_image,
            dictionary=aruco_dict
        )
        ret_val, corners = cv2.findChessboardCorners(image=self.bgr_image,
                                                     patternSize=(self.board_size, self.board_size))

        if ret_val and ids is not None:
            corners = order_points(corners, aruco_corners[0])
            self.outer_corners = np.array(
                [[corners[0][0][0], corners[0][0][1]],  # Finds the outer corners of the findChessBoardCorners points
                 [corners[self.board_size - 1][0][0], corners[self.board_size - 1][0][1]],
                 [corners[self.board_size ** 2 - self.board_size][0][0],
                  corners[self.board_size ** 2 - self.board_size][0][1]],
                 [corners[self.board_size ** 2 - 1][0][0], corners[self.board_size ** 2 - 1][0][1]]], dtype=np.float32)

            gotPose, rvec, tvec = self.find_pose(self.outer_corners)  # Find homography and draw
            if gotPose:
                R = cv2.Rodrigues(rvec)
                return True, np.block([[R[0], tvec], [0, 0, 0, 1]])
            else:
                return False, None
        else:
            return False, None

    # Generates a 2D array of board spaces A1-H8
    def gen_spaces(self):
        for i in range(self.board_size + 1):
            for j in range(self.board_size + 1):
                self.squares[i][j][0] = str(chr(97 + j)) + str(i + 1)

    def draw_spaces_and_origin(self, Mext):
        if self.bgr_display is not None:
            for i in range(self.board_size + 1):
                for j in range(self.board_size + 1):
                    pos = np.array([self.square_width / 2 + i * self.square_width,
                                    self.square_width / 2 + j * self.square_width, 0], dtype=np.float32)
                    p = self.K @ Mext @ np.block([pos, 1]).T
                    point = (int(p[0] / p[2]), int(p[1] / p[2]))
                    if self.draw_info:
                        cv2.putText(self.bgr_display, text=str(self.squares[i][j][0].decode("utf-8")),
                                    org=tuple(np.array(point) + np.array((-17, 8))),
                                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                    fontScale=0.6, color=(0, 0, 255), thickness=1, lineType=cv2.LINE_AA)

            if self.outer_corners is not None:
                found_pose, rvec, tvec = self.find_pose(self.outer_corners)
                if found_pose:
                    W = np.amax(self.corners_world, axis=0) - np.amin(self.corners_world, axis=0)
                    L = np.linalg.norm(W)
                    d = L / 5
                    p_axes = np.float32([[0, 0, 0], [d, 0, 0], [0, d, 0], [0, 0, d]])
                    p_img, J = cv2.projectPoints(objectPoints=p_axes, rvec=rvec, tvec=tvec, cameraMatrix=self.K,
                                                 distCoeffs=None)
                    p_img = p_img.reshape(-1, 2)
                    if self.draw_info:
                        cv2.line(self.bgr_display, tuple(np.int32(p_img[0])), tuple(np.int32(p_img[1])), (0, 0, 255), 2,
                                 lineType=cv2.LINE_AA)
                        cv2.line(self.bgr_display, tuple(np.int32(p_img[0])), tuple(np.int32(p_img[2])), (0, 255, 0), 2,
                                 lineType=cv2.LINE_AA)
                        cv2.line(self.bgr_display, tuple(np.int32(p_img[0])), tuple(np.int32(p_img[3])), (255, 0, 0), 2,
                                 lineType=cv2.LINE_AA)

    def click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.outer_corners is not None:
                H, _ = cv2.findHomography(self.outer_corners, self.corners_ortho)  # Finds orthophoto homography
                point = H @ [x, y, 1]  # Calculates position of mouse click point on orthophoto
                point[0] = point[0] / point[2]
                point[1] = point[1] / point[2]

                if point[0] < ((self.board_size + 1) * 100) and point[0] > 0 and point[1] < (
                        (self.board_size + 1) * 100) and point[1] > 0:
                    param.append(str(self.squares[int(point[1] / 100)][int(point[0] / 100)][0].decode("utf-8")))

    # https://stackoverflow.com/questions/40895785/using-opencv-to-overlay-transparent-image-onto-another-image
    def overlay_transparent(self, background, overlay, x, y):
        background_width = background.shape[1]
        background_height = background.shape[0]

        if x >= background_width or y >= background_height:
            return background

        h, w = overlay.shape[0], overlay.shape[1]

        if x + w > background_width:
            w = background_width - x
            overlay = overlay[:, :w]

        if y + h > background_height:
            h = background_height - y
            overlay = overlay[:h]

        if overlay.shape[2] < 4:
            overlay = np.concatenate(
                [
                    overlay,
                    np.ones((overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
                ],
                axis=2,
            )

        overlay_image = overlay[..., :overlay.shape[2]]
        mask = overlay[..., 3:] / 255.0

        background[y:y + h, x:x + w] = (1.0 - mask) * background[y:y + h, x:x + w] + mask * overlay_image

        return background

    def add_pieces_to_board(self, board_state, my_moves, selected_piece):
        # icons are in the order: K, Q, B, N, R, P
        ortho_photo_out = np.zeros((800, 800, 4), dtype=np.uint8)
        # add highlighted moves to orthophoto
        if my_moves is not None and len(my_moves) > 0:
            for move in my_moves:
                highlight_square = chess.parse_square(str(move)[2:4])
                highlight_row = highlight_square // 8
                highlight_col = highlight_square % 8
                pt1 = np.array((highlight_col * 100, highlight_row * 100))
                pt2 = pt1 + 100
                # if attack, color is red; else, color is yellow.
                if board_state[highlight_row, 7 - highlight_col] != '.':
                    color = self.attack_color
                else:
                    color = self.move_color
                ortho_photo_out = cv2.rectangle(img=ortho_photo_out, pt1=tuple(pt1), pt2=tuple(pt2),
                                                color=color, thickness=-1, lineType=cv2.LINE_AA)
        if selected_piece is not None:
            highlight_row = selected_piece // 8
            highlight_col = selected_piece % 8
            pt1 = np.array((highlight_col * 100, highlight_row * 100))
            pt2 = pt1 + 100
            ortho_photo_out = cv2.rectangle(img=ortho_photo_out, pt1=tuple(pt1), pt2=tuple(pt2),
                                            color=self.select_color, thickness=-1, lineType=cv2.LINE_AA)

        for row in range(len(board_state)):
            for col in range(len(board_state[row])):
                # add chess piece to orthophoto
                if board_state[row, col] != '.':
                    icon = self.icon_dict[board_state[row, col]]
                    ortho_photo_out = self.overlay_transparent(ortho_photo_out,
                                                               self.icons[icon[0]][icon[1]],
                                                               700 - col * 100, row * 100)
        return ortho_photo_out



    def show_image(self, window_name, board_state, my_moves, selected_piece, Mext):

        if self.outer_corners is not None and self.corners_ortho is not None and self.bgr_display is not None:
            cv2.rectangle(self.bgr_display, self.material_bar[0][0], self.material_bar[0][1], (0, 0, 0), -1)
            cv2.rectangle(self.bgr_display, self.material_bar[1][0], self.material_bar[1][1], (255, 255, 255), -1)
            self.draw_captured_pieces()

            if not self.draw_info:
                H, _ = cv2.findHomography(self.outer_corners, self.corners_ortho)  # Finds orthophoto homography
                H_inv = np.linalg.inv(H)
                ortho_photo = self.add_pieces_to_board(board_state, my_moves, selected_piece)
                warped_pieces = cv2.warpPerspective(ortho_photo, H_inv,
                                                    (self.bgr_display.shape[1], self.bgr_display.shape[0]))
                self.bgr_display = self.overlay_transparent(cv2.cvtColor(self.bgr_display, cv2.COLOR_BGR2BGRA),
                                                            warped_pieces, 0, 0)
            else:
                self.draw_spaces_and_origin(Mext)

        cv2.imshow(window_name, self.bgr_display)

    def draw_captured_pieces(self):
        white_captured = 0
        black_captured = 0
        for piece in self.captured_pieces:
            if ord(piece) >= ord('a'):
                org = (self.material_bar[1][0][0], self.material_bar[1][0][1] + self.material_dim * black_captured)
                black_captured += 1
            else:
                org = (self.material_bar[0][0][0], self.material_bar[0][0][1] + self.material_dim * white_captured)
                white_captured += 1
            icon = self.icon_dict[piece]
            self.bgr_display = self.overlay_transparent(cv2.cvtColor(self.bgr_display, cv2.COLOR_BGR2BGRA),
                                                        cv2.resize(self.icons[icon[0]][icon[1]], (20, 20)), org[0],
                                                        org[1])


def closest(lst, K):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]


def order_points(corners, aruco_location):
    aruco_center = np.array([np.average(aruco_location[0, :, 0]), np.average(aruco_location[0, :, 1])])

    corners_reshape = corners.reshape((49, 2))  # reshape to 40x2 array
    corner_dist = [np.sqrt((corner[0] - aruco_center[0]) ** 2 + (corner[1] - aruco_center[1]) ** 2) for corner in
                   corners_reshape]
    closest_val = closest([0, 1, 7, 5, 6, 13, 35, 42, 43, 41, 47, 48], np.argmin(corner_dist))

    if closest_val in [5, 6, 13]:
        corners_reshape = corners.reshape((7, 7, 2))
        corners_reshape = np.rot90(corners_reshape, 1, axes=(0, 1))
    elif closest_val in [35, 42, 43]:
        corners_reshape = corners.reshape((7, 7, 2))
        corners_reshape = np.rot90(corners_reshape, 3, axes=(0, 1))
    elif closest_val in [41, 47, 48]:
        corners_reshape = corners.reshape((7, 7, 2))
        corners_reshape = np.rot90(corners_reshape, 2, axes=(0, 1))

    return corners_reshape.reshape((49, 1, 2))
