import cv2
import mediapipe as mp
import time

# Initialize MediaPipe Hands Module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Open the default webcam
cap = cv2.VideoCapture(0)

# Set camera properties for higher FPS
cap.set(cv2.CAP_PROP_FPS, 60)  # Try to set to 60 FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set height

# Initialize FPS calculation variables
prev_time = 0
curr_time = 0

while True:
    success, frame = cap.read()
    if not success:
        break

    # Calculate FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Add text overlays
    cv2.putText(frame, "Hi there!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Hand Tracking Active", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Convert frame to RGB (MediaPipe needs RGB input)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hands
    result = hands.process(rgb_frame)

    # If hands are detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw landmarks and connections on the original frame
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Add text when hands are detected
            cv2.putText(frame, "Hand Detected!", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Show the output
    cv2.imshow("Hand Tracking", frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
