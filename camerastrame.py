import cv2
import os
from datetime import datetime
import sys

# Stream URL
stream_url = "http://192.168.12.221:8080/?action=stream"

# Save path
save_path = "captured_images"
os.makedirs(save_path, exist_ok=True)

# Open stream
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Error: Cannot open stream")
    sys.exit()

# Global frame
current_frame = None

# Button position (adjusted for smaller window)
BTN_X1, BTN_Y1 = 10, 10
BTN_X2, BTN_Y2 = 130, 45

# Mouse callback
def capture_image(event, x, y, flags, param):
    global current_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if click inside button
        if BTN_X1 <= x <= BTN_X2 and BTN_Y1 <= y <= BTN_Y2:
            if current_frame is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(save_path, f"{timestamp}.jpg")
                cv2.imwrite(filename, current_frame)
                print(f"Saved: {filename}")

# Create window
cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Camera", 640, 480)
cv2.setMouseCallback("Camera", capture_image)

print("Click CAPTURE button to save image")
print("Press 'q' or ESC to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Save original frame for capture (full quality)
    current_frame = frame.copy()

    # Resize only for display
    display_frame = cv2.resize(frame, (640, 480))

    # Draw CAPTURE button
    cv2.rectangle(display_frame, (BTN_X1, BTN_Y1), (BTN_X2, BTN_Y2), (0, 255, 0), -1)
    cv2.putText(display_frame, "CAPTURE", (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # Show window
    cv2.imshow("Camera", display_frame)

    # Key handling
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q') or key == 27:  # q or ESC
        print("Exiting...")
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
sys.exit()
