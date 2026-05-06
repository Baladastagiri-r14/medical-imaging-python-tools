import os

# Folder containing images
folder_path = r"D:\dastagiri\HDR\captured_images"

# Get list of files and sort them
files = sorted(os.listdir(folder_path))

frame_count = 1

for file in files:
    # Filter only image files
    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        old_path = os.path.join(folder_path, file)
        
        # Preserve original extension
        ext = os.path.splitext(file)[1]
        new_name = f"Frame_{frame_count}{ext}"
        new_path = os.path.join(folder_path, new_name)
        
        os.rename(old_path, new_path)
        frame_count += 1

print("Renaming completed!")
