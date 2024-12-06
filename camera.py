import depthai as dai
import cv2 
import numpy as np
# Creăm un pipeline DepthAI
pipeline = dai.Pipeline()

prevCircle = None #circle from the previous frame
dist = lambda x1,y1,x2,y2: (x1-x2)**2+(y1-y2)**2
# Adăugăm o cameră RGB la pipeline
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(1000,  700)  #camera window size
cam_rgb.setInterleaved(False)
cam_rgb.setFps(30)

# Direcționăm ieșirea camerei RGB către un nod de previzualizare
xout_rgb = pipeline.createXLinkOut()
xout_rgb.setStreamName("video")
cam_rgb.preview.link(xout_rgb.input)

# Creăm un dispozitiv DepthAI și lansăm pipeline-ul
device = dai.Device(pipeline)

# Obținem coada de ieșire pentru fluxul RGB
q_rgb = device.getOutputQueue(name="video", maxSize=4, blocking=False)

while True:
    # Citim frame-urile RGB din coadă
    in_rgb = q_rgb.get()
    frame = in_rgb.getCvFrame()

    grayFrame =  cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurFrame = cv2.GaussianBlur(grayFrame, (17,17), 0)    #cu cat pui mai mult la 17, cu atat va deveni imaginea mai blured
    
    circles= cv2.HoughCircles(blurFrame, cv2.HOUGH_GRADIENT, 1.2, 100, param1=100, param2=30, minRadius=75, maxRadius=400)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        chosen = None
        for i in circles[0, :]:
            if chosen is None: chosen =i
            if prevCircle is not None: 
                if dist(chosen[0],chosen[1],prevCircle[0],prevCircle[1])<= dist(i[0],i[1],prevCircle[0],prevCircle[1]):
                    chosen= i
        cv2.circle(frame, (chosen[0],chosen[1]), 1, (0,100,100),3)
        cv2.circle(frame, (chosen[0],chosen[1]), chosen[2], (255,0,255),3)
        prevCircle = chosen
    
                                            
    # Afișăm frame-ul folosind OpenCV
    cv2.imshow("OAK-D Lite RGB", frame)

    # Închidem fereastra dacă apăsăm ESC
    if cv2.waitKey(1) == 27:  # Escape
        break

cv2.destroyAllWindows()
