import depthai as dai
import cv2 
import numpy as np
import threading 
lock = threading.Lock()

font = cv2.FONT_HERSHEY_SIMPLEX
frontScale = 0.6
color = (0,0,255)
# Creăm un pipeline DepthAI
pipeline = dai.Pipeline()
lowerLimit = np.array([5,100,20]) #HSV
upperLimit = np.array([25,255,255])

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

def write_distance_to_file(distance):
    with lock:
        with open("distanta.txt", "w") as file:
            file.write(str(distance))

while True:
    # Citim frame-urile RGB din coadă
    in_rgb = q_rgb.get()
    frame = in_rgb.getCvFrame()
    
    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)
    #cv2.imshow("OAK-D Lite mask", mask)
    
    #grayFrame =  cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #blurFrame = cv2.GaussianBlur(grayFrame, (17,17), 0)    #cu cat pui mai mult la 17, cu atat va deveni imaginea mai blured
    
    d_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), 'uint8'), iterations=5 )
    cont,hei = cv2.findContours(d_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) #detectia conturilor ditr-o imagine binara
    cont = sorted(cont, key = cv2.contourArea , reverse = True)[:1]
    for cnt in cont:
        if (cv2.contourArea(cnt)>100 and cv2.contourArea(cnt)<306000):
            rect = cv2.minAreaRect(cnt) #face un dreptunghi rotit care se ajusteaza cat mai strans posibil in jurul conturului
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame,[box], -1, (255,0,0) ,3)
            
            pixels = rect[1][0]
            #print(pixels)
            dist = (6.5*1086)/pixels #dist = (width*focal)/pixels
            write_distance_to_file(dist)
            img = cv2.putText(frame, 'distance', (0, 20) , font, 1, color, 2, cv2.LINE_AA)
            img = cv2.putText(frame, str(dist), (110,50), font, frontScale, color,1 , cv2.LINE_AA)
                                            
    # Afișăm frame-ul folosind OpenCV
    cv2.imshow("OAK-D Lite RGB", frame)

    # Închidem fereastra dacă apăsăm ESC
    if cv2.waitKey(1) == 27:  # Escape
        break

cv2.destroyAllWindows()
