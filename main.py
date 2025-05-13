import cv2
import mediapipe as mp
import time
import numpy as np

class HandTracker:
    def __init__(self, max_hands=2, detection_confidence=0.7, tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def find_hands(self, frame, draw=True):
        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        self.results = self.hands.process(rgb_frame)
        
        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                # Draw landmarks with custom style
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        return frame

    def get_hand_positions(self, frame):
        positions = []
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    h, w, _ = frame.shape
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    landmarks.append((x, y))
                positions.append(landmarks)
        return positions

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize hand tracker
    tracker = HandTracker()
    
    # FPS calculation variables
    prev_time = 0
    fps_list = []
    
    while True:
        success, frame = cap.read()
        if not success:
            break
            
        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        
        # Smooth FPS display
        fps_list.append(fps)
        if len(fps_list) > 10:
            fps_list.pop(0)
        avg_fps = sum(fps_list) / len(fps_list)
        
        # Flip frame
        frame = cv2.flip(frame, 1)
        
        # Process frame
        frame = tracker.find_hands(frame)
        hand_positions = tracker.get_hand_positions(frame)
        
        # Add UI elements
        # Create a semi-transparent overlay for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (300, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Add text with shadow effect
        texts = [
            ("Hand Tracking", (10, 30), (0, 255, 0)),
            (f"FPS: {int(avg_fps)}", (10, 70), (0, 255, 255)),
            (f"Hands: {len(hand_positions)}", (10, 110), (255, 255, 255)),
            ("Press 'q' to quit", (10, frame.shape[0] - 20), (0, 0, 255))
        ]
        
        for text, pos, color in texts:
            # Add shadow
            cv2.putText(frame, text, (pos[0]+2, pos[1]+2), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 0, 0), 3)
            # Add main text
            cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, color, 2)
        
        # Show the output
        cv2.imshow("Hand Tracking", frame)
        
        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
