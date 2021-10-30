# C.H.E.S.S

import sys
import cv2

CAM_NUM = 0
FPS = 30


def main():
    # Initialize image capture from camera.
    video_capture = cv2.VideoCapture(CAM_NUM)  # Open video capture object
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920 / 3)   # set cam width
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080 / 3)  # set cam height

    is_ok, bgr_image_input = video_capture.read()  # Make sure we can read video
    if not is_ok:
        print("Cannot read video source")
        sys.exit()

    print("Hit ESC to quit...")

    while True:
        got_vid, bgr_image = video_capture.read()
        if not got_vid:
            break  # no camera, or reached end of video file

        # Find the chess board corners.
        ret_val, corners = cv2.findChessboardCorners(image=bgr_image, patternSize=(7, 7))

        # Draw corners on a copy of the image.
        bgr_display = bgr_image.copy()
        cv2.drawChessboardCorners(image=bgr_display, patternSize=(7, 7), corners=corners, patternWasFound=ret_val)

        # Wait for FPS frames-per-second.
        cv2.imshow('Cam Feed', bgr_display)
        key_pressed = cv2.waitKey(int(1000 / FPS))
        if key_pressed == 27:
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
