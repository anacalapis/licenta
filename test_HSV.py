import cv2
import numpy as np
import depthai as dai

def show_HSV(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = hsv[y, x]
        print(f"HSV la punctul ({x}, {y}): {pixel}")

# Pipeline DepthAI pentru RGB
pipeline = dai.Pipeline()

camRgb = pipeline.createColorCamera()
camRgb.setPreviewSize(640, 480)
camRgb.setInterleaved(False)
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)

xoutRgb = pipeline.createXLinkOut()
xoutRgb.setStreamName("rgb")
camRgb.preview.link(xoutRgb.input)

# Start device
with dai.Device(pipeline) as device:
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    while True:
        inRgb = qRgb.get()
        frame = inRgb.getCvFrame()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.imshow("Imagine", frame)
        cv2.setMouseCallback("Imagine", show_HSV)

        if cv2.waitKey(1) == 27:  # ESC
            break

cv2.destroyAllWindows()
