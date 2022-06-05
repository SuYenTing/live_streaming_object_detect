# Client: 以Socket方式接收Server端傳來的即時影像物件辨識結果 
# 並以WEB方式(flask框架)提供給使用者觀看
# 參考資料:
# https://github.com/NakulLakhotia/Live-Streaming-using-OpenCV-Flask
from flask import Flask, render_template, Response
import pickle
import socket
import struct
import cv2

app = Flask(__name__)


# 以Socket方式接收server傳來照片
def get_frames():  # generate frame by frame from camera

    # 連入socket server
    HOST = "127.0.0.1"
    PORT = 8765
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    data = b''
    payload_size = struct.calcsize("L")

    while True:

        # Retrieve message size
        while len(data) < payload_size:
            data += s.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += s.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Extract frame
        frame = pickle.loads(frame_data)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)