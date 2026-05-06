import cv2
import numpy as np
import os
from datetime import datetime
import sys
import time

# ==============================
# Stream URL
# ==============================
stream_url = "http://192.168.12.221:8080/?action=stream"

# ==============================
# Save path
# ==============================
save_path = "captured_images"
os.makedirs(save_path, exist_ok=True)

# ==============================
# Calibration file
# ==============================
calibration_file = r"D:\dastagiri\HDR\camera_calibration.xml"

# ==============================
# Load calibration
# ==============================
def load_calibration(xml_file):
    try:
        fs = cv2.FileStorage(xml_file, cv2.FILE_STORAGE_READ)
        camera_matrix = fs.getNode("camera_matrix").mat()
        dist_coeffs = fs.getNode("distortion_coefficients").mat()
        fs.release()

        if camera_matrix is None or dist_coeffs is None:
            raise Exception("Invalid file")

        print("Calibration loaded successfully")
        return camera_matrix, dist_coeffs

    except:
        print("Using fallback calibration")

        camera_matrix = np.array([
            [595.2207, 0, 828.5167],
            [0, 593.1516, 571.7868],
            [0, 0, 1]
        ], dtype=np.float64)

        dist_coeffs = np.array([
            [-0.2414565, 0.0596008, -0.00100905, 0.00262168, -0.00631019]
        ], dtype=np.float64)

        return camera_matrix, dist_coeffs


camera_matrix, dist_coeffs = load_calibration(calibration_file)

# ==============================
# Open stream
# ==============================
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Cannot open stream")
    sys.exit()

ret, frame = cap.read()
if not ret:
    print("Cannot read frame")
    sys.exit()

h, w = frame.shape[:2]

# ==============================
# Undistortion setup (ONCE)
# ==============================
new_camera_matrix = camera_matrix.copy()
new_camera_matrix[0, 0] *= 0.88
new_camera_matrix[1, 1] *= 0.7

map1, map2 = cv2.initUndistortRectifyMap(
    camera_matrix,
    dist_coeffs,
    None,
    new_camera_matrix,
    (w, h),
    cv2.CV_16SC2
)

# ==============================
# Capture control
# ==============================
capture_count = 0
last_capture_time = None
capture_delay = 10

img1_path = os.path.join(save_path, "first_image.jpg")
img2_path = os.path.join(save_path, "second_image.jpg")

img1 = None
img2 = None

# ==============================
# Window
# ==============================
cv2.namedWindow("Camera (Undistorted)", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Camera (Undistorted)", 640, 480)

print("Press 'q' or ESC to exit")

# ==============================
# Main loop
# ==============================
while True:
    ret, frame = cap.read()
    if not ret:
        print("Stream lost")
        break

    undistorted = cv2.remap(frame, map1, map2, cv2.INTER_LINEAR)

    current_time = datetime.now().timestamp()

    # ==========================
    # FIRST CAPTURE
    # ==========================
    if capture_count == 0:
        cv2.imwrite(img1_path, undistorted)
        img1 = undistorted.copy()
        print("Captured first image")

        capture_count = 1
        last_capture_time = current_time

    # ==========================
    # SECOND CAPTURE
    # ==========================
    elif capture_count == 1 and (current_time - last_capture_time) >= capture_delay:
        cv2.imwrite(img2_path, undistorted)
        img2 = undistorted.copy()
        print("Captured second image")

        capture_count = 2

        # ==========================
        # IMAGE DIFFERENCE (AUTO RUN)
        # ==========================
        print("Calculating difference...")

        img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(gray1, gray2)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        highlight = img2_resized.copy()
        highlight[thresh > 0] = [0, 0, 255]

        result_path = os.path.join(save_path, "difference.jpg")
        cv2.imwrite(result_path, highlight)

        print(f"Difference saved: {result_path}")

        cv2.imshow("Difference", highlight)

    # ==============================
    # DISPLAY STREAM
    # ==============================
    display_frame = cv2.resize(undistorted, (640, 480))
    cv2.imshow("Camera (Undistorted)", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

# ==============================
# CLEANUP
# ==============================
cap.release()
cv2.destroyAllWindows()
sys.exit()
