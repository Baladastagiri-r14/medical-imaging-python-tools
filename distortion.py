import cv2
import numpy as np
import os
import glob

class CameraCalibrator:
    def __init__(self):
        # Chessboard dimensions (number of inner corners)
        self.board_width = 9   # Adjust based on your chessboard
        self.board_height = 6  # Adjust based on your chessboard
        self.board_size = (self.board_width, self.board_height)
        
        # Size of square in real world units (mm, cm, etc.)
        self.square_size = 28.0  # Adjust to your chessboard square size in mm
        
        # Calibration flags
        self.calibration_flags = 0
        self.calibration_flags |= cv2.CALIB_FIX_K4
        self.calibration_flags |= cv2.CALIB_FIX_K5
        
    def calculate_board_corners(self):
        """Calculate 3D world coordinates of chessboard corners"""
        objp = np.zeros((self.board_width * self.board_height, 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.board_width, 0:self.board_height].T.reshape(-1, 2)
        objp = objp * self.square_size
        return objp
    
    def find_chessboard_corners_adaptive(self, image):
        """Find chessboard corners with multiple strategies"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Try different detection methods
        methods = [
            # Method 1: Standard detection
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
            # Method 2: Without adaptive threshold
            cv2.CALIB_CB_NORMALIZE_IMAGE,
            # Method 3: With FAST check
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FAST_CHECK,
            # Method 4: No flags
            0
        ]
        
        ret = False
        corners = None
        
        for flags in methods:
            ret, corners = cv2.findChessboardCorners(gray, self.board_size, flags)
            if ret:
                break
        
        # Try with image sharpening if detection fails
        if not ret:
            # Apply sharpening filter
            kernel = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]])
            sharpened = cv2.filter2D(gray, -1, kernel)
            ret, corners = cv2.findChessboardCorners(
                sharpened, self.board_size,
                cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
            )
        
        if ret:
            # Refine corner positions
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners_subpix = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            return True, corners_subpix
        
        return False, None
    
    def analyze_image_quality(self, image):
        """Analyze image quality for chessboard detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate image statistics
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        min_brightness = np.min(gray)
        max_brightness = np.max(gray)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
        
        # Check contrast
        contrast = (max_brightness - min_brightness) / 255.0
        
        print(f"    Image Analysis:")
        print(f"      Mean brightness: {mean_brightness:.1f}/255")
        print(f"      Contrast: {contrast:.2f}")
        print(f"      Edge density: {edge_density:.3f}")
        
        # Provide recommendations
        issues = []
        if contrast < 0.3:
            issues.append("Low contrast - improve lighting")
        if edge_density < 0.05:
            issues.append("Low edge density - image may be blurry")
        if mean_brightness < 80:
            issues.append("Too dark")
        elif mean_brightness > 200:
            issues.append("Too bright")
            
        if issues:
            for issue in issues:
                print(f"      ⚠️  {issue}")
        
        return contrast, edge_density, issues
    
    def enhance_image(self, image):
        """Enhance image for better chessboard detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply sharpening
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened
    
    def calibrate_from_images(self, image_folder, output_file="calibration_results.yml"):
        """Calibrate camera using images from a folder"""
        
        # Get all images from folder
        image_paths = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.JPG', '*.PNG']:
            image_paths.extend(glob.glob(os.path.join(image_folder, ext)))
        
        if not image_paths:
            print(f"No images found in {image_folder}")
            return False
        
        print(f"Found {len(image_paths)} images")
        print(f"Image folder: {image_folder}")
        print(f"Looking for chessboard pattern of size: {self.board_width} x {self.board_height}")
        print("-" * 70)
        
        # Prepare object points
        objp = self.calculate_board_corners()
        
        # Arrays to store points
        objpoints = []
        imgpoints = []
        
        # Image size
        image_size = None
        
        # Create debug directory
        debug_dir = os.path.join(image_folder, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        
        # Process each image
        successful_images = 0
        for idx, img_path in enumerate(image_paths):
            img_name = os.path.basename(img_path)
            name_without_ext = os.path.splitext(img_name)[0]
            ext = os.path.splitext(img_name)[1]
            
            print(f"\n[{idx+1}/{len(image_paths)}] Processing: {img_name}")
            
            # Read image
            img = cv2.imread(img_path)
            if img is None:
                print(f"  ❌ Failed to read image")
                continue
            
            # Get image size
            if image_size is None:
                image_size = (img.shape[1], img.shape[0])
                print(f"  Image size: {image_size[0]} x {image_size[1]}")
            
            # Analyze image quality
            contrast, edge_density, issues = self.analyze_image_quality(img)
            
            # Try detection on original image
            ret, corners = self.find_chessboard_corners_adaptive(img)
            
            # If failed, try with enhanced image
            if not ret:
                print(f"  🔧 Trying with enhanced image...")
                enhanced = self.enhance_image(img)
                ret, corners = cv2.findChessboardCorners(
                    enhanced, self.board_size,
                    cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
                )
                if ret:
                    # Refine on original grayscale
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    print(f"  ✅ Success with enhanced image!")
            
            # Try with resized image if still failing and image is large
            if not ret and (img.shape[0] > 1000 or img.shape[1] > 1000):
                print(f"  🔧 Trying with resized image...")
                scale = 0.5
                small_img = cv2.resize(img, (int(img.shape[1]*scale), int(img.shape[0]*scale)))
                ret, corners = self.find_chessboard_corners_adaptive(small_img)
                if ret:
                    # Scale corners back
                    corners = corners / scale
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    print(f"  ✅ Success with resized image!")
            
            if ret:
                print(f"  ✅ Chessboard FOUND!")
                objpoints.append(objp)
                imgpoints.append(corners)
                successful_images += 1
                
                # Draw and save debug image with corners
                img_with_corners = img.copy()
                cv2.drawChessboardCorners(img_with_corners, self.board_size, corners, ret)
                debug_path = os.path.join(debug_dir, f"{name_without_ext}_corners{ext}")
                cv2.imwrite(debug_path, img_with_corners)
                print(f"  💾 Saved: {os.path.basename(debug_path)}")
                
            else:
                print(f"  ❌ Chessboard NOT found")
                if issues:
                    print(f"  💡 Issues detected: {', '.join(issues)}")
                else:
                    print(f"  💡 Chessboard pattern may not be fully visible or dimensions may be incorrect")
                
                # Save debug image showing why detection failed
                debug_img = img.copy()
                cv2.putText(debug_img, "Pattern NOT detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(debug_img, f"Contrast: {contrast:.2f}, Edge density: {edge_density:.3f}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Show edge detection to help diagnose
                gray_display = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray_display, 50, 150)
                edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                
                # Resize for display if too large
                if debug_img.shape[1] > 800:
                    scale = 800 / debug_img.shape[1]
                    new_width = int(debug_img.shape[1] * scale)
                    new_height = int(debug_img.shape[0] * scale)
                    debug_img = cv2.resize(debug_img, (new_width, new_height))
                    edges_colored = cv2.resize(edges_colored, (new_width, new_height))
                
                debug_vis = np.hstack([debug_img, edges_colored])
                debug_path = os.path.join(debug_dir, f"{name_without_ext}_debug_failed{ext}")
                cv2.imwrite(debug_path, debug_vis)
                print(f"  💾 Debug image saved: {os.path.basename(debug_path)}")
        
        print("\n" + "="*70)
        print(f"SUMMARY: Successfully detected chessboard in {successful_images}/{len(image_paths)} images")
        print("="*70)
        
        if successful_images < 5:
            print(f"\n⚠️  Only {successful_images} good images found. Recommended: at least 10-15 images.")
            print("\nTroubleshooting suggestions:")
            print("1. Check the debug images in the 'debug' folder")
            print("2. Verify chessboard dimensions are correct")
            print("3. Ensure chessboard is flat and fully visible")
            print("4. Try taking photos from different angles")
            print("5. Improve lighting and focus")
            return False
        
        # Perform camera calibration
        print("\n🔧 Performing camera calibration...")
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, image_size, None, None, flags=self.calibration_flags
        )
        
        if ret:
            print("\n✅ Calibration SUCCESSFUL!")
            print(f"📊 Reprojection error: {ret:.6f} pixels")
            print("\n📷 Camera Matrix:")
            print(camera_matrix)
            print("\n🔧 Distortion Coefficients:")
            print(dist_coeffs.ravel())
            
            # Calculate individual errors
            print("\n📊 Per-image reprojection errors:")
            total_error = 0
            for i in range(len(objpoints)):
                imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
                error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
                total_error += error
                print(f"  Image {i+1}: {error:.4f} pixels")
            
            print(f"\n📈 Mean reprojection error: {total_error/len(objpoints):.4f} pixels")
            
            # Save results
            self.save_calibration(output_file, camera_matrix, dist_coeffs, image_size, ret)
            
            return True, camera_matrix, dist_coeffs
        else:
            print("\n❌ Calibration FAILED!")
            return False, None, None
    
    def save_calibration(self, filename, camera_matrix, dist_coeffs, image_size, rms_error):
        """Save calibration results"""
        # Save as YAML
        fs = cv2.FileStorage(filename, cv2.FILE_STORAGE_WRITE)
        fs.write("calibration_date", cv2.getTickCount())
        fs.write("image_width", image_size[0])
        fs.write("image_height", image_size[1])
        fs.write("board_width", self.board_width)
        fs.write("board_height", self.board_height)
        fs.write("square_size", self.square_size)
        fs.write("camera_matrix", camera_matrix)
        fs.write("distortion_coefficients", dist_coeffs)
        fs.write("reprojection_error", rms_error)
        fs.release()
        
        # Save as text
        txt_filename = filename.replace('.yml', '.txt')
        with open(txt_filename, 'w') as f:
            f.write("Camera Calibration Results\n")
            f.write("="*50 + "\n\n")
            f.write(f"Image Size: {image_size[0]} x {image_size[1]}\n")
            f.write(f"Chessboard: {self.board_width} x {self.board_height}\n")
            f.write(f"Square Size: {self.square_size} mm\n")
            f.write(f"Reprojection Error: {rms_error:.6f}\n\n")
            f.write("Camera Matrix:\n")
            f.write(str(camera_matrix) + "\n\n")
            f.write("Distortion Coefficients:\n")
            f.write(str(dist_coeffs.ravel()) + "\n")
        
        print(f"\n💾 Results saved to: {filename} and {txt_filename}")

def main():
    # Your image path
    image_folder = r"D:\dastagiri\HDR\captured_images"
    
    # Create calibrator
    calibrator = CameraCalibrator()
    
    print("\n" + "="*70)
    print("CHESSBOARD CALIBRATION TOOL")
    print("="*70)
    
    # Ask for chessboard dimensions
    print("\nPlease enter your chessboard dimensions (inner corners):")
    print("Example: If you have 10x7 squares, inner corners = 9x6")
    
    try:
        width = int(input("Number of inner corners horizontally (width): "))
        height = int(input("Number of inner corners vertically (height): "))
        calibrator.board_width = width
        calibrator.board_height = height
        calibrator.board_size = (width, height)
    except:
        print("Using default dimensions: 9x6")
        print("If this is incorrect, restart the script")
    
    square_size_input = input(f"\nEnter square size in mm (default {calibrator.square_size}): ")
    if square_size_input:
        try:
            calibrator.square_size = float(square_size_input)
        except:
            pass
    
    print("\n" + "="*70)
    print("CAMERA CALIBRATION SETTINGS")
    print("="*70)
    print(f"📁 Image folder: {image_folder}")
    print(f"🎯 Chessboard dimensions: {calibrator.board_width} x {calibrator.board_height} (inner corners)")
    print(f"📏 Square size: {calibrator.square_size} mm")
    print("="*70)
    
    # Check if folder exists
    if not os.path.exists(image_folder):
        print(f"\n❌ Error: Folder '{image_folder}' does not exist!")
        return
    
    # Perform calibration
    success, camera_matrix, dist_coeffs = calibrator.calibrate_from_images(
        image_folder, 
        output_file="calibration_results.yml"
    )
    
    if success:
        print("\n✨ Calibration completed successfully!")
        print("\nGenerated files:")
        print("  📄 calibration_results.yml - OpenCV format")
        print("  📄 calibration_results.txt - Human readable")
        print("  📁 debug/ - Folder with debug images")
        
        # Optional: Test undistortion on a sample image
        test = input("\nDo you want to test undistortion on a sample image? (y/n): ")
        if test.lower() == 'y':
            sample_image = input("Enter image filename (or press Enter for first image): ")
            if not sample_image:
                # Get first image from folder
                image_files = glob.glob(os.path.join(image_folder, "*.jpg")) + \
                            glob.glob(os.path.join(image_folder, "*.png"))
                if image_files:
                    sample_image = image_files[0]
            
            if os.path.exists(sample_image):
                img = cv2.imread(sample_image)
                h, w = img.shape[:2]
                new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(
                    camera_matrix, dist_coeffs, (w, h), 1, (w, h)
                )
                undistorted = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)
                
                # Display results
                cv2.imshow("Original", img)
                cv2.imshow("Undistorted", undistorted)
                print("Press any key to close windows...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print(f"Image not found: {sample_image}")
    else:
        print("\n❌ Calibration failed.")
        print("\nPlease check the debug images in the 'debug' folder to understand why detection failed.")
        print("\nCommon solutions:")
        print("1. Make sure the ENTIRE chessboard is visible in each photo")
        print("2. Ensure good lighting with no glare")
        print("3. Keep the chessboard flat and in focus")
        print("4. Take 15-20 photos from different angles")
        print("5. Verify your chessboard dimensions are correct")

if __name__ == "__main__":
    main()
