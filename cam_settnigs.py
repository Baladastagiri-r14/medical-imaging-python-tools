import cv2
import numpy as np
import requests
import time
from threading import Thread
from urllib3.exceptions import IncompleteRead

class ESP32CAMStream:
    def __init__(self, url="http://192.168.4.1:81/stream", timeout=5):
        self.url = url
        self.timeout = timeout
        self.frame = None
        self.stopped = False
        self.stream = None
        self.byte_buffer = bytes()
        self.control_url = url.replace("/stream", "/control")
        
        # Default camera settings
        self.settings = {
            'framesize': 10,       # UXGA (1600x1200)
            'quality': 10,          # Quality (0-63)
            'brightness': 0,        # (-2 to 2)
            'contrast': 0,          # (-2 to 2)
            'saturation': 0,        # (-2 to 2)
            'special_effect': 0,    # (0-6)
            'awb': 1,               # Auto White Balance (0-1)
            'awb_gain': 1,          # (0-1)
            'wb_mode': 0,           # (0-4)
            'aec': 1,               # Auto Exposure Control (0-1)
            'aec2': 0,              # (0-1)
            'ae_level': 0,          # (-2 to 2)
            'aec_value': 300,       # (0-1200)
            'agc': 1,               # Auto Gain Control (0-1)
            'agc_gain': 0,          # (0-30)
            'gainceiling': 0,       # (0-6)
            'bpc': 0,               # Black Pixel Correction (0-1)
            'wpc': 1,               # White Pixel Correction (0-1)
            'raw_gma': 1,           # (0-1)
            'lenc': 1,              # Lens Correction (0-1)
            'hmirror': 0,           # Horizontal Mirror (0-1)
            'vflip': 0,             # Vertical Flip (0-1)
            'dcw': 1,               # Downsize EN (0-1)
            'colorbar': 0           # Color Bar (0-1)
        }

    def update_camera_setting(self, var, value):
        """Update a single camera setting"""
        try:
            if var in self.settings:
                self.settings[var] = value
                requests.get(f"{self.control_url}?var={var}&val={value}", timeout=2)
                print(f"Set {var} to {value}")
            else:
                print(f"Invalid setting: {var}")
        except Exception as e:
            print(f"Failed to set {var}: {e}")

    def apply_camera_settings(self):
        """Apply all stored camera settings"""
        for var, value in self.settings.items():
            self.update_camera_setting(var, value)

    def start(self):
        self.apply_camera_settings()  # Apply settings before starting
        Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            try:
                self.stream = requests.get(self.url, stream=True, timeout=self.timeout)
                
                for chunk in self.stream.iter_content(chunk_size=1024):
                    if self.stopped:
                        break
                        
                    self.byte_buffer += chunk
                    a = self.byte_buffer.find(b'\xff\xd8')
                    b = self.byte_buffer.find(b'\xff\xd9')
                    
                    if a != -1 and b != -1:
                        jpg = self.byte_buffer[a:b+2]
                        self.byte_buffer = self.byte_buffer[b+2:]
                        
                        if len(jpg) > 0:
                            try:
                                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                                if img is not None:
                                    self.frame = img
                            except Exception as e:
                                print(f"Decoding error: {e}")
                                continue
                                
            except (requests.exceptions.RequestException, IncompleteRead) as e:
                print(f"Stream error: {e}")
                time.sleep(2)
                self.byte_buffer = bytes()
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(2)

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        if self.stream:
            self.stream.close()

def display_menu():
    print("\nESP32-CAM Control Menu")
    print("1. Change Resolution")
    print("2. Adjust Quality")
    print("3. Set Brightness")
    print("4. Set Contrast")
    print("5. Set Saturation")
    print("6. Toggle AWB (Auto White Balance)")
    print("7. Toggle AEC (Auto Exposure)")
    print("8. Toggle Mirror/Flip")
    print("9. Reset to Defaults")
    print("0. Exit Menu")
    return input("Select option: ")

if __name__ == "__main__":
    esp32_cam_url = "http://192.168.4.1:81/stream"
    stream = ESP32CAMStream(esp32_cam_url).start()
    
    try:
        while True:
            frame = stream.read()
            
            if frame is not None:
                # Original and upscaled views
                #cv2.imshow("Original Stream", frame)
                upscaled = cv2.resize(frame, (1280, 960), interpolation=cv2.INTER_CUBIC)
                cv2.imshow("Upscaled Stream", upscaled)
                
                
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('m'):
                while True:
                    choice = display_menu()
                    
                    if choice == '1':
                        res = input("Resolution (6:VGA, 7:SVGA, 8:XGA, 9:HD, 10:UXGA): ")
                        stream.update_camera_setting('framesize', int(res))
                    elif choice == '2':
                        qual = input("Quality (0-63, lower=better): ")
                        stream.update_camera_setting('quality', int(qual))
                    elif choice == '3':
                        bright = input("Brightness (-2 to 2): ")
                        stream.update_camera_setting('brightness', int(bright))
                    elif choice == '4':
                        contrast = input("Contrast (-2 to 2): ")
                        stream.update_camera_setting('contrast', int(contrast))
                    elif choice == '5':
                        sat = input("Saturation (-2 to 2): ")
                        stream.update_camera_setting('saturation', int(sat))
                    elif choice == '6':
                        awb = 1 if stream.settings['awb'] == 0 else 0
                        stream.update_camera_setting('awb', awb)
                    elif choice == '7':
                        aec = 1 if stream.settings['aec'] == 0 else 0
                        stream.update_camera_setting('aec', aec)
                    elif choice == '8':
                        mirror = 1 if stream.settings['hmirror'] == 0 else 0
                        flip = 1 if stream.settings['vflip'] == 0 else 0
                        stream.update_camera_setting('hmirror', mirror)
                        stream.update_camera_setting('vflip', flip)
                    elif choice == '9':
                        stream.apply_camera_settings()
                    elif choice == '0':
                        break
                    
    finally:
        stream.stop()
        cv2.destroyAllWindows()
