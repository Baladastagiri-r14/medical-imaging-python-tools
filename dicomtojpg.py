import os
import pydicom
from PIL import Image
import numpy as np

def dicom_to_jpg(dicom_path, jpg_path):
    # Read DICOM file
    dicom = pydicom.dcmread(dicom_path)

    # Get pixel data
    pixel_data = dicom.pixel_array

    # Apply histogram equalization
    equalized_image = histogram_equalization(pixel_data)

    # Convert to PIL Image
    image = Image.fromarray(equalized_image)

    # Save as JPG
    if image.mode == 'L':
        image.save(jpg_path)
    else:
        # Convert to 'L' (grayscale) if not already in grayscale
        image.convert('L').save(jpg_path)

def histogram_equalization(image):
    # Flatten the image array
    flat_image = image.flatten()

    # Calculate histogram
    histogram, bins = np.histogram(flat_image, bins=256, range=(0, 256))

    # Cumulative distribution function
    cdf = histogram.cumsum()
    
    # Check if max value of CDF is not zero
    if cdf.max() == 0:
        return image

    cdf_normalized = cdf / cdf.max()

    # Equalization
    equalized_image = np.interp(flat_image, bins[:-1], cdf_normalized * 255)
    equalized_image = equalized_image.reshape(image.shape)

    return equalized_image.astype(np.uint8)

# Paths to DICOM and JPG folders
dicom_folder = r"D:\3d images\circular\DICOM"
jpg_folder = r"D:\3d images\circular\DICOM_CPNG"

# Iterate through DICOM files in the folder
for filename in os.listdir(dicom_folder):
    if filename.endswith('.dcm'):
        dicom_path = os.path.join(dicom_folder, filename)
        jpg_filename = os.path.splitext(filename)[0] + '.jpg'
        jpg_path = os.path.join(jpg_folder, jpg_filename)
        dicom_to_jpg(dicom_path, jpg_path)
