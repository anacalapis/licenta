import depthai as dai
import cv2
import numpy as np

drawing = False
ix, iy = -1, -1
rx, ry, rw, rh = 0, 0, 0, 0
roi_selected = False
reset_roi = False

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, roi_selected, rx, ry, rw, rh
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            rx, ry = min(ix, x), min(iy, y)
            rw, rh = abs(ix - x), abs(iy - y)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        roi_selected = True

width, height = 1280, 720
pipeline = dai.Pipeline()
camRgb = pipeline.createColorCamera()
camRgb.setPreviewSize(width, height)
camRgb.setInterleaved(False)
camRgb.setFps(30)

xoutRgb = pipeline.createXLinkOut()
xoutRgb.setStreamName("rgb")
camRgb.preview.link(xoutRgb.input)

with dai.Device(pipeline) as device:
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    roi_hist = None
    track_window = None
    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

    cv2.namedWindow("Tracking")
    cv2.setMouseCallback("Tracking", draw_rectangle)

    while True:
        inRgb = qRgb.get()
        frame = inRgb.getCvFrame()
        clone = frame.copy()

        if not roi_selected and drawing:
            cv2.rectangle(clone, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 2)
        elif roi_selected and roi_hist is None:
            roi = frame[ry:ry+rh, rx:rx+rw]
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
            roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0,180])
            cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
            track_window = (rx, ry, rw, rh)
            continue

        if roi_hist is not None:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            back_proj = cv2.calcBackProject([hsv], [0], roi_hist, [0,180], 1)
            ret, track_window = cv2.CamShift(back_proj, track_window, term_crit)
            pts = cv2.boxPoints(ret)
            pts = np.int0(pts)
            clone = cv2.polylines(clone, [pts], True, (0,255,0), 2)

        cv2.imshow("Tracking", clone)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC = exit
            break
        elif key == ord('r'):  # 'r' = reset tracking
            roi_selected = False
            roi_hist = None
            track_window = None
            print("🔁 Selectează din nou obiectul.")


cv2.destroyAllWindows()
