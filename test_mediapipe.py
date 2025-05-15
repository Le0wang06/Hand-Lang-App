import mediapipe as mp
import cv2

def test_mediapipe():
    try:
        # Test MediaPipe initialization
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands()
        print("✅ MediaPipe Hands initialized successfully")
        
        # Test OpenCV
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera opened successfully")
            ret, frame = cap.read()
            if ret:
                print("✅ Frame captured successfully")
            cap.release()
        else:
            print("❌ Failed to open camera")
            
        print("\nMediaPipe version:", mp.__version__)
        print("OpenCV version:", cv2.__version__)
        
    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    test_mediapipe() 