import cv2
import sys

# This program captures images of a chessboard, finds corners, and saves the images.
# Note that the chessboard must have an unequal number of rows and columns.
CAMERA_NUMBER = 0       # 0 is the default camera
PATTERN_SIZE = (7, 6)


def create_named_window(window_name, image):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    h = image.shape[0]
    w = image.shape[1]

    WIN_MAX_SIZE = 1000
    if max(w, h) > WIN_MAX_SIZE:
        scale = WIN_MAX_SIZE / max(w, h)
    else:
        scale = 1
    cv2.resizeWindow(winname=window_name, width=int(w*scale), height=int(h*scale))


def main():
    # Initialize image capture from camera.
    video_capture = cv2.VideoCapture(CAMERA_NUMBER)  # Open video capture object
    is_ok, bgr_image_input = video_capture.read()  # Make sure we can read video
    if not is_ok:
        print("Cannot read video source")
        sys.exit()

    print("Hit ESC to quit; any other key to capture an image ...")
    imageNum = 0
    while True:
        is_ok, bgr_image_input = video_capture.read()
        if not is_ok:
            break  # no camera, or reached end of video file

        gray_image = cv2.cvtColor(src=bgr_image_input, code=cv2.COLOR_BGR2GRAY)

        # Find the chess board corners.
        ret_val, corners = cv2.findChessboardCorners(image=gray_image, patternSize=PATTERN_SIZE)

        # Draw corners on a copy of the image.
        bgr_display = bgr_image_input.copy()
        cv2.drawChessboardCorners(image=bgr_display, patternSize=PATTERN_SIZE, corners=corners, patternWasFound=ret_val)

        # Wait for xx msec (0 = wait till keypress).
        create_named_window('img', bgr_display)
        cv2.imshow('img', bgr_display)
        key_pressed = cv2.waitKey(30)
        if key_pressed == -1:
            continue
        elif key_pressed == 27:
            break
        else:
            fname = "img%02d.png" % imageNum
            cv2.imwrite(filename=fname, img=bgr_image_input)
            print("Saving image %s" % fname)
            imageNum += 1

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
