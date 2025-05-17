from flask import Flask, Response
import cv2
import mediapipe as mp

app = Flask(__name__)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

def generate_frames():
    camera = cv2.VideoCapture(0)
    with mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        model_complexity=1
    ) as hands:
        try:
            while True:
                success, frame = camera.read()
                if not success:
                    break
                # Flip for natural selfie view
                frame = cv2.flip(frame, 1)
                # Convert to RGB for MediaPipe
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)
                # Draw hand landmarks
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_styles.get_default_hand_landmarks_style(),
                            mp_styles.get_default_hand_connections_style()
                        )
                # Encode as JPEG
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