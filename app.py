from flask import Flask, Response, jsonify
import cv2
import mediapipe as mp
import time

app = Flask(__name__)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# --- Camera Setup (singleton) ---
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
if not camera.isOpened():
    raise RuntimeError("Could not open camera.")

def classify_hand_sign(landmarks):
    if not landmarks:
        return "No Hand"
    tips = [landmarks[i] for i in [4, 8, 12, 16, 20]]
    palm = landmarks[0]
    if all(abs(tip[1] - palm[1]) < 0.1 for tip in tips):
        return "Fist"
    if all(abs(tip[1] - palm[1]) > 0.3 for tip in tips):
        return "Open Palm"
    if (abs(landmarks[8][1] - palm[1]) > 0.3 and
        abs(landmarks[12][1] - palm[1]) > 0.3 and
        abs(landmarks[16][1] - palm[1]) < 0.15 and
        abs(landmarks[20][1] - palm[1]) < 0.15):
        return "Peace"
    return "Unknown"

def generate_frames():
    with mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        model_complexity=0
    ) as hands:
        prev_time = time.time()
        while True:
            success, frame = camera.read()
            if not success:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            num_hands = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
            sign_text = "No Hand"
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_styles.get_default_hand_landmarks_style(),
                        mp_styles.get_default_hand_connections_style()
                    )
                    h, w, _ = frame.shape
                    landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
                    sign_text = classify_hand_sign(landmarks)
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
            prev_time = curr_time
            cv2.putText(frame, f'Hands: {num_hands}', (10, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, f'FPS: {int(fps)}', (10, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Sign: {sign_text}', (10, 115),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>Camera Feed</title>
            <style>
                body { margin: 0; padding: 20px; background: #000; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
                .container { max-width: 1200px; width: 100%; }
                img { width: 100%; height: auto; border-radius: 8px; }
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

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

import atexit
@atexit.register
def cleanup():
    if camera.isOpened():
        camera.release()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True) 