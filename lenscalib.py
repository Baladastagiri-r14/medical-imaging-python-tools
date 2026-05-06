import cv2
import numpy as np
import glob
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom


def fisheye_calibration(image_folder, chessboard_size=(8, 5), square_size=28.0):
    """
    Perform camera calibration using chessboard images
    """

    # Prepare object points
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    objp = objp * square_size

    objpoints = []
    imgpoints = []

    # Get all images
    image_paths = []
    for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']:
        image_paths.extend(glob.glob(os.path.join(image_folder, ext)))
    image_paths = list(set(image_paths))

    print(f"Found {len(image_paths)} unique images")

    successful_images = []
    image_size = None

    for image_path in image_paths:
        img = cv2.imread(image_path)
        if img is None:
            continue

        if image_size is None:
            image_size = (img.shape[1], img.shape[0])

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(
            gray,
            chessboard_size,
            None,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        )

        if ret:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            objpoints.append(objp)
            imgpoints.append(corners2)
            successful_images.append(image_path)
            print(f"✓ {os.path.basename(image_path)}")
        else:
            print(f"✗ {os.path.basename(image_path)}")

    print(f"\nSuccessfully detected: {len(successful_images)}/{len(image_paths)} images")

    if len(objpoints) < 10:
        print(f"⚠️ Only {len(objpoints)} images. Need at least 10-15 for good calibration.")
        if len(objpoints) < 3:
            print("❌ Insufficient images!")
            return None

    print("\nPerforming camera calibration...")

    try:
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, image_size, None, None
        )

        print("✅ Calibration successful!")
        print(f"Reprojection error: {ret:.6f}")

        k1, k2, p1, p2, k3 = dist_coeffs[0]
        print("\nDistortion coefficients:")
        print(f"k1 = {k1:.6f}")
        print(f"k2 = {k2:.6f}")
        print(f"p1 = {p1:.6f}")
        print(f"p2 = {p2:.6f}")
        print(f"k3 = {k3:.6f}")

        return {
            'camera_matrix': camera_matrix,
            'dist_coeffs': dist_coeffs,
            'rms': ret,
            'image_size': image_size,
            'successful_images': len(successful_images)
        }

    except Exception as e:
        print(f"Calibration failed: {str(e)}")
        return None


def save_calibration_xml(calibration_data, output_path="camera_calibration.xml"):
    root = ET.Element("opencv_storage")

    camera_matrix_elem = ET.SubElement(root, "camera_matrix", type_id="opencv-matrix")
    ET.SubElement(camera_matrix_elem, "rows").text = "3"
    ET.SubElement(camera_matrix_elem, "cols").text = "3"
    ET.SubElement(camera_matrix_elem, "dt").text = "d"

    cm_data = calibration_data['camera_matrix'].flatten()
    ET.SubElement(camera_matrix_elem, "data").text = " ".join([f"{x:.12e}" for x in cm_data])

    dist_elem = ET.SubElement(root, "distortion_coefficients", type_id="opencv-matrix")
    ET.SubElement(dist_elem, "rows").text = "1"
    ET.SubElement(dist_elem, "cols").text = "5"
    ET.SubElement(dist_elem, "dt").text = "d"

    dc_data = calibration_data['dist_coeffs'].flatten()
    ET.SubElement(dist_elem, "data").text = " ".join([f"{x:.12e}" for x in dc_data])

    xml_str = ET.tostring(root, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    print(f"\n✅ Calibration saved to: {output_path}")


def correct_images_alpha0(calibration_data, image_folder):
    image_paths = []
    for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']:
        image_paths.extend(glob.glob(os.path.join(image_folder, ext)))
    image_paths = list(set(image_paths))

    output_dir = "corrected_images_alpha0"
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("CORRECTING IMAGES WITH ALPHA=0 (CROPPED)")
    print("=" * 60)

    h, w = calibration_data['image_size'][1], calibration_data['image_size'][0]

    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
        calibration_data['camera_matrix'],
        calibration_data['dist_coeffs'],
        (w, h),
        0,
        (w, h)
    )

    print(f"Original image size: {w} x {h}")

    if roi != (0, 0, 0, 0):
        x, y, w_roi, h_roi = roi
        print(f"Cropped image size: {w_roi} x {h_roi}")

    print(f"\nProcessing {len(image_paths)} images...")

    for idx, image_path in enumerate(image_paths, 1):
        img = cv2.imread(image_path)
        if img is None:
            continue

        undistorted = cv2.undistort(
            img,
            calibration_data['camera_matrix'],
            calibration_data['dist_coeffs'],
            None,
            new_camera_matrix
        )

        if roi != (0, 0, 0, 0):
            x, y, w_roi, h_roi = roi
            undistorted = undistorted[y:y + h_roi, x:x + w_roi]

        base_name = os.path.splitext(os.path.basename(image_path))[0]
        save_path = os.path.join(output_dir, f"{base_name}_corrected.jpg")
        cv2.imwrite(save_path, undistorted)

        print(f"[{idx}/{len(image_paths)}] ✓ {base_name}")

    print(f"\n✅ All corrected images saved to: {output_dir}/")


def print_calibration_values(calibration_data):
    print("\n" + "=" * 60)
    print("CAMERA MATRIX AND DISTORTION COEFFICIENTS")
    print("=" * 60)

    print("\nCamera Matrix:")
    print(calibration_data['camera_matrix'])

    print("\nDistortion Coefficients:")
    print(calibration_data['dist_coeffs'])


def main():
    image_folder = r"D:\dastagiri\HDR\Capture"
    chessboard_size = (8, 5)
    square_size = 28.0

    print("=" * 60)
    print("CAMERA CALIBRATION")
    print("=" * 60)

    if not os.path.exists(image_folder):
        print(f"❌ Folder not found: {image_folder}")
        return

    calibration_data = fisheye_calibration(image_folder, chessboard_size, square_size)

    if calibration_data:
        print_calibration_values(calibration_data)
        save_calibration_xml(calibration_data)

        with open("calibration_values.txt", "w") as f:
            f.write(str(calibration_data))

        print("\n✅ Calibration values saved")

        choice = input("\nDo you want to correct images? (y/n): ").strip().lower()
        if choice == 'y':
            correct_images_alpha0(calibration_data, image_folder)
    else:
        print("❌ Calibration failed!")


if __name__ == "__main__":
    main()
