import cv2
import dxcam

camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Could not open webcam.")
    exit()

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:

        # Get the pixel from the current frame
        b, g, r = frame[y, x]

        # Convert pixel to HSV
        pixel = frame[y, x]
        hsv_pixel = cv2.cvtColor(
            pixel.reshape(1, 1, 3),
            cv2.COLOR_BGR2HSV
        )[0, 0]

        # Convert captured-image coordinates to desktop coordinates
        desktop_x = x
        desktop_y = y

        print(f"Captured coordinates: ({x}, {y})")
        print(f"Desktop coordinates: ({desktop_x}, {desktop_y})")
        print(f"RGB: ({r}, {g}, {b})")
        print(f"HSV: ({hsv_pixel[0]}, {hsv_pixel[1]}, {hsv_pixel[2]})")
        print()

cv2.namedWindow("Screen")
cv2.setMouseCallback("Screen", mouse_callback)

while True:
    ret, frame = camera.read()

    if not ret:
        print("Could not read frame.")
        break

    if frame is None:
        continue

    cv2.imshow("Screen", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()