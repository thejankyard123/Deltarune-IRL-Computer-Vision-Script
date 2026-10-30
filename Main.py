# Thanks for checking out the video! Like, comment, and subscribe if you haven't already!
# I am by no means a software engineer and this is definitely vibecoded so don't make fun of me too much for any mistakes lol
# Make sure to review the comments in this script to adjust any settings that I had configured for my setup that may be different for yours.
# Make sure to have cv2, numpy, dxcam, and pynput installed before running this script
# Have fun!

import cv2
import numpy as np
import dxcam
from pynput.keyboard import Key, Controller

keyboard = Controller()

def main():

    # Error threshold for movement detection. If you have a wider FOV camera and a larger area to move in, consider lowering this to make the program more sensitive
    error = 0.05

    # Deltarune Settings
    # Bounds for the screen capture on Deltarune in pixels. I sized these for my 1920x1080 resolution, so adjust accordiningly if you have a different resolution monitor.
    # This also assumes that the game is running on the leftmost monitor, so you may need to offset the LEFT value if your game is not.
    left = 0
    top = 0
    right = 1920
    bottom = 715

    # Bounds for detecting the Soul in Deltarune
    lRed= np.array([0, 250, 125])
    uRed = np.array([5, 255, 255])

    # Bounds for detecting the BattleBox in Deltarune
    lGreen = np.array([39, 145, 70])
    uGreen = np.array([65, 255, 255])

    # Virtual Camera that does the Deltarune screen recording
    cameraDR = dxcam.create(output_color="BGR")

    # IRL Settings
    # Red can occupy both really high and really low H values, so I used two sets of red bounds to catch both extremes for IRL detection
    # The STL file for the headband I created can be found in the GITHUB repository alongside this script. I highly recommend using a printed hat or a colored baseball cap for better tracking.
    # You will likely need to adjust these values based on the exact color of your hat, your camera, and your lighting conditions.
    lRed1 = np.array([170, 70, 100])
    uRed1 = np.array([180, 270, 270])
    lRed2 = np.array([0, 70, 100])
    uRed2 = np.array([5, 270, 270])

    # Bounds for detecting the painter's tape battlebox
    # Just like the red bounds, you will probably need to adjust these based on your tape, camera, and lighting conditions
    lBlue = np.array([95, 55, 20])
    uBlue = np.array([130, 250, 175])

    # IRL Camera. Change the index if your webcam is not at index 1
    cameraIRL = cv2.VideoCapture(1)

    # Error message if your webcame is not opened
    if not cameraIRL.isOpened():
        print("Could not open webcam.")
        exit()

    # Initial positions
    lastPosDR = (0, 0)
    lastPosIRL = (0, 0)

    # Booleans that track if a key is currently pressed
    rPressed = False
    lPressed = False
    uPressed = False
    dPressed = False

    # Loop for everything
    while True:
        # Grab the DR frame
        frameDR = cameraDR.grab(region=(left, top, right, bottom))
        
        if frameDR is None:
            print("Could not read DR frame") # Debugging check
            continue

        ret, frameIRL = cameraIRL.read()

        if not ret:
            print("Could not read IRL frame") # Debugging check
            break

        #frameIRL = cv2.flip(frameIRL, 1)  # Uncomment this line to flip the frame horizontally (1) or vertically (0) depending on your camera orientation

        # Reads the position of the soul in Deltarune, see function definition later in the script
        deltaruneX, deltaruneY = DeltaruneVision(frameDR, lastPosDR, lRed, uRed, 
                                                   lGreen, uGreen, right, left, bottom, top)
        lastPosDR = (deltaruneX, deltaruneY)

        #print(f"Deltarune Position: ({deltaruneX}, {deltaruneY})") # Debugging statement, uncomment line for troubleshooting
        
        # Reads your position IRL, see function definition later in the script
        cameraX, cameraY = CameraVision(frameIRL, lastPosIRL, lRed1, uRed1, lRed2, uRed2, lBlue, uBlue)
        lastPosIRL = (cameraX, cameraY)

        #print(f"Camera Position: ({cameraX}, {cameraY})") # Debugging statement, uncomment line for troubleshooting

        # Don't do anything if either vision system delivers a blank value
        # Controls the keyboard based on the relative positions of the red SOUL in Deltarune and the webcam
        if not(
            deltaruneX is None or
            deltaruneY is None or
            cameraX is None or
            cameraY is None):

            # Right movement
            if cameraX > deltaruneX + error:
                if not rPressed:
                    keyboard.press(Key.right)
                    rPressed = True
            elif cameraX < deltaruneX + error:
                if rPressed:
                    keyboard.release(Key.right)
                    rPressed = False

            # Left movement
            if cameraX < deltaruneX - error:
                if not lPressed:
                    keyboard.press(Key.left)
                    lPressed = True
            elif cameraX > deltaruneX - error:
                if lPressed:
                    keyboard.release(Key.left)
                    lPressed = False

            # Up movement
            if cameraY < deltaruneY - error:
                if not uPressed:
                    keyboard.press(Key.up)
                    uPressed = True
            elif cameraY > deltaruneY - error:
                if uPressed:
                    keyboard.release(Key.up)
                    uPressed = False

            # Down movement
            if cameraY > deltaruneY + error:
                if not dPressed:
                    keyboard.press(Key.down)
                    dPressed = True
            elif cameraY < deltaruneY + error:
                if dPressed:
                    keyboard.release(Key.down)
                    dPressed = False

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Clean up
    cv2.destroyAllWindows()
    cameraDR.release()
    cameraIRL.release()


# Function that reads and returns the position of the soul in Deltarune
def DeltaruneVision(frame, lastPos, lRed, uRed, lGreen, uGreen, right, left, bottom, top):

    # Soul detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Masks and countours red objects in the bounds
    redMask = cv2.inRange(
        hsv,
        lRed,
        uRed
    )

    redContours, _ = cv2.findContours(
        redMask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    rawSoulPos = None

    if redContours:

        # Keep only red contours that are roughly the size of the soul, avoids detecting things like enemies as the soul. You may have to change this area threshhold for different resolutions
        validRedContours = [
            contour
            for contour in redContours
            if cv2.boundingRect(contour)[2] <= 40
            and cv2.boundingRect(contour)[3] <= 40
            and cv2.contourArea(contour) > 100
        ]

        if validRedContours:

            # Find largest valid red object, avoids detecting things like small red attacks as the soul.
            soulContour = max(
                validRedContours,
                key=cv2.contourArea
            )

            # Rectangle around the soul
            x, y, w, h = cv2.boundingRect(soulContour)

            # Finds center of rectangle
            soulX = x + w // 2
            soulY = y + h // 2

            rawSoulPos = (soulX, soulY)

            # Draws rectangle around the soul
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (255, 0, 255),
                2
            )

            # Draws center point
            cv2.circle(
                frame,
                rawSoulPos,
                5,
                (255, 0, 255),
                -1
            )

            # Displays coordinates
            cv2.putText(
                frame,
                f"SOUL: ({soulX}, {soulY})",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 255),
                2
            )


    # Battlebox Detection, works very similarly to soul detection
    greenMask = cv2.inRange(
        hsv,
        lGreen,
        uGreen
    )

    greenContours, _ = cv2.findContours(
        greenMask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    box = None

    validGreenContours = [
        contour
        for contour in greenContours
        if cv2.contourArea(contour) > 100
    ]

    if validGreenContours:

        # Finds the most extreme bounds across all valid green contours. This allows the battlebox to be detected even when it is split or partially covered by an attack in game.
        minX = min(
            cv2.boundingRect(contour)[0]
            for contour in validGreenContours
        )

        minY = min(
            cv2.boundingRect(contour)[1]
            for contour in validGreenContours
        )

        maxX = max(
            cv2.boundingRect(contour)[0]
            + cv2.boundingRect(contour)[2]
            for contour in validGreenContours
        )

        maxY = max(
            cv2.boundingRect(contour)[1]
            + cv2.boundingRect(contour)[3]
            for contour in validGreenContours
        )

        boxW = maxX - minX
        boxH = maxY - minY

        # Makes sure the box is sufficiently large to reasonably be the battlebox
        if boxW > 150 and boxH > 150:

            boxX = minX
            boxY = minY

            box = (
                boxX,
                boxY,
                boxW,
                boxH
            )

            # Draws battle box
            cv2.rectangle(
                frame,
                (boxX, boxY),
                (maxX, maxY),
                (100, 255, 0),
                3
            )

            # Displays dimensions
            cv2.putText(
                frame,
                f"BOX: x={boxX}, y={boxY}, "
                f"w={boxW}, h={boxH}",
                (boxX, boxY - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )


    # Logic for returning the souls position
    if rawSoulPos is not None:
        if box is not None:
            boxX, boxY, boxW, boxH = box

            # Calculate relative position of the soul within the battle box
            relX = (rawSoulPos[0] - boxX) / boxW
            relY = (rawSoulPos[1] - boxY) / boxH
        else:
            relX = (rawSoulPos[0]) / (right - left)
            relY = (rawSoulPos[1]) / (bottom - top)
    else:
        if box is not None:
            relX, relY = lastPos
        else:
            relX = None
            relY = None

    # Shows the tracking frames
    cv2.imshow(
        "Deltarune Position Tracker",
        frame
    )

    # Returns position
    return relX, relY

# Function that reads and returns the IRL position.
def CameraVision(frame, lastPos, lRed1, uRed1, lRed2, uRed2, lBlue, uBlue):
    # Soul detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Includes both <180 and >0 H values for red detection
    redMask1 = cv2.inRange(hsv, lRed1, uRed1)
    redMask2 = cv2.inRange(hsv, lRed2, uRed2)
    redMask = cv2.bitwise_or(redMask1, redMask2)

    redContours, _ = cv2.findContours(
        redMask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    rawRedPos = None

    if redContours:
        # Find largest valid red object
        soulContour = max(
            redContours,
            key=cv2.contourArea
        )

        # Rectangle around the soul
        x, y, w, h = cv2.boundingRect(soulContour)

        # Center of rectangle
        soulX = x + w // 2
        soulY = y + h // 2

        rawRedPos = (soulX, soulY)

        # Draws rectangle around the soul
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (255, 0, 255),
            2
        )

        # Draws center point
        cv2.circle(
            frame,
            rawRedPos,
            5,
            (255, 0, 255),
            -1
        )

        # Displays coordinates
        cv2.putText(
            frame,
            f"SOUL: ({soulX}, {soulY})",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 255),
            2
        )

        # Battlebox detection
        blueMask = cv2.inRange(
            hsv,
            lBlue,
            uBlue
        )

        blueContours, _ = cv2.findContours(
            blueMask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
    
        box = None
   
        # Disregards blue regions that are not large enough to be considered the battle box
        validBlueContours = [
           contour
           for contour in blueContours
           if cv2.contourArea(contour) > 100
        ]
   
        if validBlueContours:
   
           # Find extreme edges across all contours. This protects against situations like if my arm is covering part of the battlebox
           minX = min(
               cv2.boundingRect(contour)[0]
               for contour in validBlueContours
           )
   
           minY = min(
               cv2.boundingRect(contour)[1]
               for contour in validBlueContours
           )
   
           maxX = max(
               cv2.boundingRect(contour)[0]
               + cv2.boundingRect(contour)[2]
               for contour in validBlueContours
           )
   
           maxY = max(
               cv2.boundingRect(contour)[1]
               + cv2.boundingRect(contour)[3]
               for contour in validBlueContours
           )
   
           boxW = maxX - minX
           boxH= maxY - minY
   
           # Checks if the final battle box is large enough to reasonably be considered the battlebox
           if boxW > 150 and boxH > 150:
   
               boxX = minX
               boxY = minY
   
               box = (
                   boxX,
                   boxY,
                   boxW,
                   boxH
               )
   
               # Draws battle box
               cv2.rectangle(
                   frame,
                   (boxX, boxY),
                   (maxX, maxY),
                   (100, 255, 0),
                   3
               )
   
               # Displays dimensions
               cv2.putText(
                   frame,
                   f"BOX: x={boxX}, y={boxY}, "
                   f"w={boxW}, h={boxH}",
                   (boxX, boxY - 10),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.6,
                   (0, 255, 0),
                   2
               )

    if rawRedPos is not None:
        if box is not None:
            boxX, boxY, boxW, boxH = box

            # Calculate relative soul position inside the battlebox
            relX = (rawRedPos[0] - boxX) / boxW
            relY = (rawRedPos[1] - boxY) / boxH
        else:
            relX, relY = lastPos
    else:
        relX, relY = lastPos

    cv2.imshow("Camera Detection", frame)

    return relX, relY

if __name__ == "__main__":
    main()