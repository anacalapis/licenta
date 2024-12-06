import cv2
import depthai as dai
import numpy as np

# Setăm pipeline-ul DepthAI
pipeline = dai.Pipeline()

# Adăugăm camera color
camRgb = pipeline.createColorCamera()
camRgb.setPreviewSize(640, 480)
camRgb.setInterleaved(False)
camRgb.setFps(30)

# Adăugăm modulul de adâncime
monoLeft = pipeline.createMonoCamera()
monoRight = pipeline.createMonoCamera()
stereo = pipeline.createStereoDepth()

monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
stereo.setLeftRightCheck(True)
stereo.setSubpixel(True)

# Conectăm camerele monocrome la modulul de adâncime
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)

# Trimitem fluxul video și de adâncime către gazdă
xoutVideo = pipeline.createXLinkOut()
xoutVideo.setStreamName("video")
camRgb.preview.link(xoutVideo.input)

xoutDepth = pipeline.createXLinkOut()
xoutDepth.setStreamName("depth")
stereo.depth.link(xoutDepth.input)

# Funcție de selecție a obiectului
def select_object(event, x, y, flags, param):
    global bbox, selecting, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        selecting = True
        bbox = [x, y, x, y]
    elif event == cv2.EVENT_MOUSEMOVE and selecting:
        bbox[2:] = [x, y]
    elif event == cv2.EVENT_LBUTTONUP:
        selecting = False

# Variabile globale
bbox = None
selecting = False
tracker = None

# Pornim dispozitivul
with dai.Device(pipeline) as device:
    videoQueue = device.getOutputQueue(name="video", maxSize=4, blocking=False)
    depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

    cv2.namedWindow("Video")
    cv2.setMouseCallback("Video", select_object)

    while True:
        videoFrame = videoQueue.get()
        frame = videoFrame.getCvFrame()

        depthFrame = depthQueue.get().getFrame()
        depthFrameColor = cv2.normalize(depthFrame, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_JET)

        if bbox and not selecting:
            # Dacă obiectul este selectat, inițializăm tracker-ul
            if tracker is None:
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, tuple(bbox))
            else:
                # Actualizăm tracker-ul
                success, box = tracker.update(frame)
                if success:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                    # Calculăm distanța medie din regiunea urmărită
                    depthRegion = depthFrame[y:y+h, x:x+w]
                    if depthRegion.size > 0:
                        meanDepth = np.mean(depthRegion[np.nonzero(depthRegion)])  # Ignorăm 0-urile
                        distance = meanDepth / 10  # Convertim din mm în cm
                        cv2.putText(frame, f"Dist: {distance:.2f} cm", (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    tracker = None  # Dacă tracking-ul eșuează, resetează tracker-ul

        # Desenează dreptunghiul în timpul selecției
        if selecting and bbox:
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

        # Afișăm cadrele video și de adâncime
        cv2.imshow("Video", frame)
        cv2.imshow("Depth", depthFrameColor)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('r'):  # Resetăm selecția
            bbox = None
            tracker = None

    cv2.destroyAllWindows()
