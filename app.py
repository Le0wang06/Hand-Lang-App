from flask import Flask, Response
import cv2

app = Flask(__name__)

def generate_frames():
    camera = cv2.VideoCapture(0)
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                # Flip the frame horizontally for a more natural view
                frame = cv2.flip(frame, 1)
                
                # Convert to JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        camera.release()

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>Camera Feed</title>
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    background: #000;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }
                .container {
                    max-width: 800px;
                    width: 100%;
                }
                img {
                    width: 100%;
                    height: auto;
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <img src="/video_feed" alt="Camera Feed">
            </div>
        </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True) 