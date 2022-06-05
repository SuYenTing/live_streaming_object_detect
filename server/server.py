# Server: Youtube直播即時影像物件偵測 並以Socket將辨識結果傳輸給Client端
# 參考資料: 
# https://abhitronix.github.io/vidgear/v0.2.5-stable/gears/camgear/usage/
# https://github.com/jonec76/w14_socket
# https://stackoverflow.com/questions/59587166/send-webcam-stream-from-server-in-python-using-sockets
from vidgear.gears import CamGear
import cv2
import threading
import socket
import pickle
import struct

# 讀取自製函數
from yolo_detect import yolo_detect


# Youtube直播即時影像物件偵測
def stream_detect():

    global outputFrame

    # 相關參數設定
    # 每n偵執行一次辨識(依機器效能決定偵數)
    frame_per_detection = 5
    # 設定串流解析度
    options = {"STREAM_RESOLUTION": "480p"}

    # Add YouTube Video URL as input source and enable Stream Mode (`stream_mode = True`)
    stream = CamGear(
        source="https://www.youtube.com/watch?v=z_mlibCfgFI",
        stream_mode=True,
        logging=True,
        **options
    ).start()

    # loop over
    img_counter = 0  # 計偵器
    while True:

        # read frames from stream
        frame = stream.read()
        img_counter += 1

        # check for frame if Nonetype
        if frame is None:
            break

        # 為避免效能延遲 每n偵才執行辨識
        if img_counter % frame_per_detection == 0:

            # 執行Yolo物件偵測
            outputFrame = yolo_detect(frame, yoloConfidence=0.2)

    # safely close video stream
    stream.stop()


# 建立socket server
class Server:
    
    def __init__(self):
        self.start_server()


    def start_server(self):

        HOST = "127.0.0.1"
        PORT = 8765
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        self.s.listen(5)
    
        print('Running on host: '+str(HOST))
        print('Running on port: '+str(PORT))

        while True:
            c, addr = self.s.accept()
            threading.Thread(target=self.send_img_to_client, args=(c, addr, )).start()


    # 傳輸影像到client socket
    def send_img_to_client(self, c, addr):
        while True:
            data = pickle.dumps(outputFrame)
            message_size = struct.pack("L", len(data))
            try:
                c.sendall(message_size + data)
            except:
                break


if __name__ == '__main__':

    # 執行Youtube直播即時影像物件偵測
    threading.Thread(target=stream_detect).start()

    # 建立socket server
    server = Server()

    # # 以opencv方式呈現辨識結果
    # outputFrame = None
    # while True:

    #     # Show output window
    #     if outputFrame is not None:
    #         cv2.imshow("Output", outputFrame)

    #         # check for 'q' key if pressed
    #         key = cv2.waitKey(1) & 0xFF
    #         if key == ord("q"):
    #             break

    # # close output window
    # cv2.destroyAllWindows()
