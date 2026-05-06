import cv2
import numpy as np
import requests
import time
from threading import Thread

class ESP32CAMStream:
    def __init__(self, url="http://192.168.4.1:81/stream"):
        self.url = url
        self.frame = None
        self.stopped = False
        self.byte_buffer = bytes()
        self.chunk_size = 1024  # Default for VGA
        self.frame_count = 0
        self.last_debug = time.time()

    def start(self):
        Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            try:
                with requests.get(self.url, stream=True, timeout=5) as r:
                    for chunk in r.iter_content(chunk_size=self.chunk_size):
                        if self.stopped:
                            break
                            
                        self.byte_buffer += chunk
                        a = self.byte_buffer.find(b'\xff\xd8')  # JPEG start
                        b = self.byte_buffer.find(b'\xff\xd9')  # JPEG end
                        
                        if a != -1 and b != -1:
                            jpg = self.byte_buffer[a:b+2]
                            self.byte_buffer = self.byte_buffer[b+2:]
                            
                            if len(jpg) > 1000:  # Skip very small "frames" (errors)
                                try:
                                    img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                                    if img is not None:
                                        self.frame = img
                                        self.frame_count += 1
                                        
                                        # Dynamic chunk size adjustment
                                        if len(jpg) > 20000:  # If frames are large
                                            self.chunk_size = min(8192, self.chunk_size * 2)
                                        elif len(jpg) < 5000:   # If frames are small
                                            self.chunk_size = max(1024, self.chunk_size // 2)
                                except Exception as e:
                                    print(f"Decode error: {e}")
                                    
                            # Debug output every 2 seconds
                            if time.time() - self.last_debug > 2:
                                avg_size = len(jpg) if 'jpg' in locals() else 0
                                print(f"FPS: {self.frame_count/2:.1f} | Chunk: {self.chunk_size} | JPEG: {avg_size} bytes")
                                self.frame_count = 0
                                self.last_debug = time.time()
                                
            except Exception as e:
                print(f"Stream error: {e}")
                time.sleep(2)  # Reconnect delay
                self.byte_buffer = bytes()  # Reset buffer

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

if __name__ == "__main__":
    stream = ESP32CAMStream().start()
    try:
        while True:
            frame = stream.read()
            if frame is not None:
                cv2.imshow("ESP32-CAM VGA Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        stream.stop()
        cv2.destroyAllWindows()
