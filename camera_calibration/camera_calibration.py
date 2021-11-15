import numpy as np
import cv2
import glob
import os


PATTERN_SIZE = (7, 6)


# Utility function to create an image window.
def create_named_window(window_name, image):
    # WINDOW_NORMAL allows resize; use WINDOW_AUTOSIZE for no resize.
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    h = image.shape[0]  # image height
    w = image.shape[1]  # image width
    # Shrink the window if it is too big (exceeds some maximum size).
    WIN_MAX_SIZE = 1000
    if max(w, h) > WIN_MAX_SIZE:
        scale = WIN_MAX_SIZE / max(w, h)
    else:
        scale = 1
    cv2.resizeWindow(winname=window_name, width=int(w * scale), height=int(h * scale))


# This program reads images of a chessboard, finds corners, and calibrates the camera.
# The chessboard is assumed to be 7 rows and 8 columns of squares.

# Create points in target coordinates; i.e., (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0).
# These are the inner corners of the squares. Note that it doesn't find the outer corners, so the actual
# grid is 6 x 7 corners. Units don't matter because we are not interested in the absolute camera poses.
target_pts = np.zeros((6 * 7, 3), np.float32)
target_pts[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = []  # Collect all 3d points in target coordinates
imgpoints = []  # Collect all 2d points in image plane
images = glob.glob('camera_calibration/cam_images/*.png')     # Get list of filenames in this folder
if len(images) == 0:
    print('Images not found.')
    exit()
img = cv2.imread(images[0])
h, w, _ = img.shape
del img

for fname in images:
    img = cv2.imread(fname)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray_image.shape
    # Find the chess board corners
    ret_val, corners = cv2.findChessboardCorners(gray_image, PATTERN_SIZE, None)
    # If found, add object and image points.
    if ret_val == True:
        print(fname)
        # Optionally refine corner locations.
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv2.cornerSubPix(gray_image, corners, (11, 11), (-1, -1), criteria)
        # Collect the object and image points.
        objpoints.append(target_pts)
        imgpoints.append(corners2)
        # Draw and display the corners
        cv2.drawChessboardCorners(img, PATTERN_SIZE, corners2, ret_val)
        # cv2.imshow('img', img)
        # cv2.waitKey(0)

cv2.destroyAllWindows()
# Do the calibration.
ret_val, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    objectPoints=objpoints, imagePoints=imgpoints, imageSize=(w, h),
    cameraMatrix=None, distCoeffs=None)

print("Camera matrix:")
print(repr(K))
print("Distortion coeffs:")
print(repr(dist))
print()

cam_mat_filename = 'camera_matrix.csv'
np.savetxt(os.path.join('camera_calibration', cam_mat_filename), K, delimiter=',')
print(f"Saved camera matrix as '{cam_mat_filename}'")

dist_coeff_filename = 'dist_coeff.csv'
np.savetxt(os.path.join('camera_calibration', dist_coeff_filename), dist, delimiter=',')
print(f"Saved distortion coefficients as '{dist_coeff_filename}'")

# Calculate re-projection error - should be close to zero.
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], K, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error
print( "total error: {}".format(mean_error/len(objpoints)) )

# Optionally undistort and display the images.
for fname in images:
    img = cv2.imread(fname)
    cv2.imshow("distorted", img)
    create_named_window("distorted", img)
    undistorted_img = cv2.undistort(src=img, cameraMatrix=K, distCoeffs=dist)

    cv2.imshow("undistorted", undistorted_img)
    create_named_window("undistorted", undistorted_img)
    cv2.imwrite("undistorted_" + fname, undistorted_img)

    if cv2.waitKey(0) == 27:  # ESC is ascii code 27
        break

