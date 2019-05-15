from flask import Flask, render_template, Response

# Raspberry Pi camera module (requires picamera package, developed by Miguel Grinberg)
#from camera_pi import Camera
import cv2
app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen():
    camera=cv2.VideoCapture(0)
    """Video streaming generator function."""
    while True:
#        frame = camera.get_frame()
        retval, frame = camera.read()
        imgencode=cv2.imencode('.jpg',frame)[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + stringData + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False, threaded=False)