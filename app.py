from flask import Flask, Response, jsonify
import cv2
import mediapipe as mp
import time
import numpy as np
import os

app = Flask(__name__)

collected_data = []  # List of [x1, y1, z1, ..., x21, y21, z21, label]

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# --- Camera Setup (singleton) ---
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
if not camera.isOpened():
    raise RuntimeError("Could not open camera.")

def clear_terminal():
    """Clear terminal screen based on OS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_landmarks(hand_landmarks, hand_num):
    """Print landmarks to terminal in a formatted way."""
    print(f"\n=== Hand {hand_num + 1} Landmarks ===")
    print("Index | X      | Y      | Z      | Visibility")
    print("-" * 45)
    for idx, landmark in enumerate(hand_landmarks.landmark):
        print(f"{idx:5d} | {landmark.x:6.3f} | {landmark.y:6.3f} | {landmark.z:6.3f} | {landmark.visibility:6.3f}")

def process_hand_landmarks(hand_landmarks):
    """Process hand landmarks and return normalized coordinates."""
    landmarks = []
    for landmark in hand_landmarks.landmark:
        landmarks.append({
            'x': landmark.x,
            'y': landmark.y,
            'z': landmark.z,
            'visibility': landmark.visibility
        })
    return landmarks

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
            
            if results.multi_hand_landmarks:
                # Clear terminal and print new coordinates
                clear_terminal()
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    print_landmarks(hand_landmarks, i)
                    
                    # Draw landmarks on frame
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_styles.get_default_hand_landmarks_style(),
                        mp_styles.get_default_hand_connections_style()
                    )
                    
                    # Add landmark numbers and coordinates
                    h, w, _ = frame.shape
                    for idx, landmark in enumerate(hand_landmarks.landmark):
                        cx, cy = int(landmark.x * w), int(landmark.y * h)
                        # Display landmark number
                        cv2.putText(frame, str(idx), (cx, cy), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                        
                        # Display coordinates below the landmark number
                        coord_text = f"x:{landmark.x:.2f} y:{landmark.y:.2f} z:{landmark.z:.2f}"
                        cv2.putText(frame, coord_text, (cx, cy + 15), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
            prev_time = curr_time
            
            cv2.putText(frame, f'Hands: {num_hands}', (10, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, f'FPS: {int(fps)}', (10, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
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
            <title>Hand Tracking</title>
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

@app.route('/landmarks')
def get_landmarks():
    success, frame = camera.read()
    if not success:
        return jsonify({"error": "Could not read frame"}), 500
        
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    with mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        model_complexity=0
    ) as hands:
        results = hands.process(rgb)
        
        if not results.multi_hand_landmarks:
            return jsonify({"hands": []})
            
        hands_data = []
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = process_hand_landmarks(hand_landmarks)
            hands_data.append(landmarks)
            
        return jsonify({
            "hands": hands_data,
            "num_hands": len(hands_data)
        })

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

import atexit
@atexit.register
def cleanup():
    if camera.isOpened():
        camera.release()
        
@app.route('/collect_sample', methods=['POST'])
def collect_sample():
    from flask import request
    label = request.args.get('label')
    if not label:
        return jsonify({"error": "Missing label"}), 400

    success, frame = camera.read()
    if not success:
        return jsonify({"error": "Could not read frame"}), 500

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    ) as hands:
        results = hands.process(rgb)
        if not results.multi_hand_landmarks:
            return jsonify({"error": "No hand detected"}), 400

        hand_landmarks = results.multi_hand_landmarks[0]
        row = []
        for lm in hand_landmarks.landmark:
            row += [lm.x, lm.y, lm.z]

        row.append(label)
        collected_data.append(row)
        return jsonify({"status": "sample collected", "label": label, "total": len(collected_data)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True) 