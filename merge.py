import cv2
import numpy as np
import requests
import time
import socket
import struct
from threading import Thread

# === Server (stream from ESP32-CAM, display locally, send via TCP with timestamp) ===
class ESP32CAMStreamTCPServer:
    def __init__(self, url="http://192.168.4.1:81/stream", tcp_ip='127.0.0.1', tcp_port=9999):
        self.url = url
        self.frame = None
        self.stopped = False
        self.byte_buffer = bytes()
        self.chunk_size = 1024
        self.frame_count = 0
        self.last_debug = time.time()

        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        self.client_socket = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.tcp_ip, self.tcp_port))
        self.server_socket.listen(1)
        print(f"[Server] Waiting for TCP client to connect at {self.tcp_ip}:{self.tcp_port} ...")

    def start(self):
        Thread(target=self.update, daemon=True).start()
        Thread(target=self.tcp_handler, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            try:
                with requests.get(self.url, stream=True, timeout=5) as r:
                    for chunk in r.iter_content(chunk_size=self.chunk_size):
                        if self.stopped:
                            break
                        self.byte_buffer += chunk
                        a = self.byte_buffer.find(b'\xff\xd8')
                        b = self.byte_buffer.find(b'\xff\xd9')
                        if a != -1 and b != -1:
                            jpg = self.byte_buffer[a:b+2]
                            self.byte_buffer = self.byte_buffer[b+2:]
                            if len(jpg) > 1000:
                                try:
                                    img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                                    if img is not None:
                                        self.frame = img
                                        self.frame_count += 1

                                        # Display server local frame
                                        cv2.imshow("Server Local View", self.frame)
                                        if cv2.waitKey(1) & 0xFF == ord('q'):
                                            self.stop()
                                            return

                                        if len(jpg) > 20000:
                                            self.chunk_size = min(8192, self.chunk_size * 2)
                                        elif len(jpg) < 5000:
                                            self.chunk_size = max(1024, self.chunk_size // 2)
                                except Exception as e:
                                    print(f"[Server] Decode error: {e}")

                            if time.time() - self.last_debug > 2:
                                avg_size = len(jpg)
                                print(f"[Server] FPS: {self.frame_count/2:.1f} | Chunk: {self.chunk_size} | JPEG: {avg_size} bytes")
                                self.frame_count = 0
                                self.last_debug = time.time()
            except Exception as e:
                print(f"[Server] Stream error: {e}")
                time.sleep(2)
                self.byte_buffer = bytes()

    def tcp_handler(self):
        self.client_socket, addr = self.server_socket.accept()
        print(f"[Server] Client connected from {addr}")

        while not self.stopped:
            if self.frame is not None:
                ret, jpeg = cv2.imencode('.jpg', self.frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ret:
                    data = jpeg.tobytes()
                    try:
                        timestamp = time.time()
                        ts_bytes = struct.pack('d', timestamp)  # 8 bytes timestamp
                        length = len(data)
                        length_bytes = length.to_bytes(4, byteorder='big')

                        # Send: [timestamp (8 bytes)] + [length (4 bytes)] + [jpeg bytes]
                        self.client_socket.sendall(ts_bytes + length_bytes + data)
                    except Exception as e:
                        print(f"[Server] TCP send error: {e}")
                        break
            time.sleep(0.03)

        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        print("[Server] Client disconnected")

    def stop(self):
        self.stopped = True
        self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()

# === Client (receive frames over TCP and display with delay print) ===
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def tcp_client(tcp_ip='127.0.0.1', tcp_port=9999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((tcp_ip, tcp_port))
    print("[Client] Connected to server")

    try:
        while True:
            ts_bytes = recvall(sock, 8)
            if ts_bytes is None:
                print("[Client] Server disconnected")
                break
            timestamp = struct.unpack('d', ts_bytes)[0]

            length_bytes = recvall(sock, 4)
            if length_bytes is None:
                print("[Client] Server disconnected")
                break
            length = int.from_bytes(length_bytes, byteorder='big')

            frame_data = recvall(sock, length)
            if frame_data is None:
                print("[Client] Server disconnected")
                break

            delay = time.time() - timestamp
            #print(f"[Client] Delay: {delay*1000:.1f} ms")

            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                cv2.imshow('TCP Video Stream (Client)', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        sock.close()
        cv2.destroyAllWindows()
        print("[Client] Connection closed")

if __name__ == "__main__":
    stream_server = ESP32CAMStreamTCPServer().start()
    client_thread = Thread(target=tcp_client, daemon=True)
    client_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        stream_server.stop()
        cv2.destroyAllWindows()
