import cv2
import os

# Open the default camera
cam = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cam.isOpened():
    print("Error: Could not open camera")
    exit()

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"Camera opened successfully. Resolution: {frame_width}x{frame_height}")
print("Press 'r' to start/stop recording")
print("Press 'q' to quit")

# Initialize recording variables
is_recording = False
out = None

while True:
    ret, frame = cam.read()
    
    if not ret:
        print("Error: Failed to grab frame")
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Handle recording
    if is_recording:
        out.write(frame)
        # Draw recording indicator
        cv2.putText(frame, "REC", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the captured frame
    cv2.imshow('Camera', frame)

    # Handle key presses
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('r'):
        if not is_recording:
            # Start recording
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))
            is_recording = True
            print("Recording started")
        else:
            # Stop recording
            is_recording = False
            if out is not None:
                out.release()
                out = None
            print("Recording stopped")

# Release the capture and writer objects
cam.release()
if out is not None:
    out.release()

# Delete the output file if it exists
if os.path.exists('output.mp4'):
    os.remove('output.mp4')
    print("Output file deleted")

cv2.destroyAllWindows()