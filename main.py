import cv2

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
print("Press 'q' to quit")

while True:
    ret, frame = cam.read()
    
    if not ret:
        print("Error: Failed to grab frame")
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Display the captured frame
    cv2.imshow('Camera', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture
cam.release()
cv2.destroyAllWindows()