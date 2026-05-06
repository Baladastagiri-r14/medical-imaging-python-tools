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

    def start(self):
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
                    a = self.byte_buffer.find(b'\xff\xd8')  # JPEG start
                    b = self.byte_buffer.find(b'\xff\xd9')  # JPEG end
                    
                    if a != -1 and b != -1:
                        jpg = self.byte_buffer[a:b+2]
                        self.byte_buffer = self.byte_buffer[b+2:]
                        
                        # Verify the JPEG is valid before decoding
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
                time.sleep(2)  # Wait before reconnecting
                self.byte_buffer = bytes()  # Clear buffer
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(2)

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        if self.stream:
            self.stream.close()

if __name__ == "__main__":
    # Replace with your ESP32-CAM's IP address
    esp32_cam_url = "http://192.168.4.1:81/stream"
    
    stream = ESP32CAMStream(esp32_cam_url).start()
    
    try:
        while True:
            frame = stream.read()
            
            if frame is not None:
                #cv2.imshow("ESP32-CAM Stream", frame)
                upscaled = cv2.resize(frame, (1280, 960), interpolation=cv2.INTER_CUBIC)
                cv2.imshow("Upscaled Stream", upscaled)
                
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        stream.stop()
        cv2.destroyAllWindows()
