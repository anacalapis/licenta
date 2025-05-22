import depthai as dai
import cv2
import numpy as np
import math
import threading 
import time
from datetime import datetime

lock = threading.Lock()
def write_distance_to_file(X, Y):
    with lock:
        with open("distanta.txt", "w") as file:
            
            distA = math.sqrt((X + 68.5)**2 + (Y +6)**2) #coord inelA (-68.5,-6)
            distB = math.sqrt((X - 70)**2 + (Y -9.5)**2) #coord inelB (70, 9.5)
          
            file.write(f'A{round(distA,3)}B{round(distB,3)}')
            distA = f"{round(distA,3)}"
            distB = f"{round(distB,3)}"
            
            cv2.putText(clone, distA, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0, 255, 0), 2)
            cv2.putText(clone, distB, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0, 255, 0), 2)
            

# Global variables for ROI selection
conturare_obiect = False
coord_init_click_X, coord_init_click_Y = -1, -1
rx, ry, rw, rh = 0, 0, 0, 0
obiect_selectat = False
limita_inferioara_culoare = None
limita_superioară_culoare = None

def draw_rectangle(event, x, y, flags, param):          #funcție specifică OpenCV care monitorizează evenimentele mouse-ului
    #x, y reprezintă coordonatele curente ale mouse-ului
    global coord_init_click_X, coord_init_click_Y                       #coordonatele inițiale în momentul în care se apasă pe mouse pt a începe selecția
    global conturare_obiect                      #este de tip boolean și indică dacă se desenează conturul, în acel moment
    global obiect_selectat                 #devine adevărată atunci când s-a selectat o bucată din imagine
    global rx, ry                       #coordonatele colțului din stânga sus
    global rw, rh                       #lățimea și lungimea dreptunghiului
    global limita_inferioara_culoare, limita_superioară_culoare       #limita inferioară și superioară al intervalului de valori a culorii selectate în HSV
    if event == cv2.EVENT_LBUTTONDOWN:  #când este apăsat butonul stâng al mouse-ului, înseamnă că începe selectarea obiectului
        conturare_obiect = True                  #se pune variabila pe adevărat
        coord_init_click_X, coord_init_click_Y = x, y                            #se salvează coordonatele unde s-a dat click prima dată pe imagine pentru a începe selecția
    elif event == cv2.EVENT_MOUSEMOVE:                                           #dacă mouse-ul se mișcă și s-a început selecția
        if conturare_obiect:                                                     #indică începutul selecții
            rx, ry = min(coord_init_click_X, x), min(coord_init_click_Y, y)      #se actualizează în permanență coordonatele colțului din stânga-sus
            rw, rh = abs(coord_init_click_X - x), abs(coord_init_click_Y - y)    #se actualizează în permanență lungimea și lățimea dreptunghiului ce urmează să se formeze
    elif event == cv2.EVENT_LBUTTONUP:                                           #dacă nu se mai ține butonul stâng apăsat, înseamnă că selecția obiectului s-a terminat
        conturare_obiect = False                                                 #indică terminarea efectuării conturului
        obiect_selectat = True                                                   #indică existența unei zone deja selectate (regiune de interes)
        roi = hsvFrame[ry:ry+rh, rx:rx+rw]                                       #se extrage zona selectată, în format HSV  
        h, s, v = cv2.split(roi)                                                 #separă cele 3 canale (HSV) ale imaginii color într-o listă

        limita_inferioara_culoare = np.array([                                   #np.mean(h)- calculează media valorii acelei liste și astfel se obține o valoare medie, 
                                                                                 #a fiecărui canal, utilizată la calcularea intervalului
            max(0, np.mean(h) - 10),                                             #se adaugă o toleranța pentru limita inferioară la canalul corespunzător nuanței
            max(0, np.mean(s) - 30),                                             #se adaugă o toleranța pentru limita inferioară la canalul corespunzător saturației
            max(0, np.mean(v) - 30)                                              #se adaugă o toleranța pentru limita inferioară la canalul corespunzător valorii luminozității
        ]).astype(np.uint8)                                                      #convertește la un vector de uint8, care poate lua valori de la 0 la 255
        
        limita_superioară_culoare = np.array([
            min(180, np.mean(h) + 10),                                           #se adaugă o toleranța pentru limita superioară la canalul corespunzător nuanței
            min(255, np.mean(s) + 30),                                           #se adaugă o toleranța pentru limita superioară la canalul corespunzător saturației
            min(255, np.mean(v) + 30)                                            #se adaugă o toleranța pentru limita superioară la canalul corespunzător valorii luminozității
        ]).astype(np.uint8)
        
        print(f"Intervalul de culoare [ {limita_inferioara_culoare} , {limita_superioară_culoare}]")    #se afișează, în terminal, intervalul obținut

def draw_origin(imagine_curentă, centru_img_X, centru_img_Y):
   
    #pe imaginea curentă, în punctul de coordonate (centru_img_X , centru_img_Y), se desenează cu alb, un X, de dimensiunea 20 și grosimea de 2 pixeli
    cv2.drawMarker(imagine_curentă, (centru_img_X, centru_img_Y), (255, 255, 255), cv2.MARKER_CROSS, 20, 2)
    
    #pe imaginea curentă, desenează o line roșie și groasă de 2 pixeli, de la punctul (centru_img_X , centru_img_Y) la (centru_img_X+50 , centru_img_Y) pentru a ilustra care este axa X pe imagine
    cv2.line(imagine_curentă, (int(centru_img_X), int(centru_img_Y)), (int(centru_img_X + 50), int(centru_img_Y)), (0, 0, 255), 2)
    
    #pe imaginea curentă, se scrie un X la punctul (centru_img_X+55 , centru_img_Y) cu fontul FONT_HERSHEY_SIMPLEX, dimensiune de 0.5, de culoarea roșie și grosimea de 2 pixeli
    #pentru a indica că acea linie roșie semnifică axa X
    cv2.putText(imagine_curentă, "X", (int(centru_img_X + 55), int(centru_img_Y + 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    #pe imaginea curentă, desenează o line verde și groasă de 2 pixeli, de la punctul (centru_img_X , centru_img_Y) la (centru_img_X , centru_img_Y-50) pentru a ilustra care este axa Y pe imagine
    cv2.line(imagine_curentă, (int(centru_img_X), int(centru_img_Y)), (int(centru_img_X), int(centru_img_Y - 50)), (0, 255, 0), 2)
    #pe imaginea curentă, se scrie un Y la punctul (centru_img_X-15 , centru_img_Y-55) cu fontul FONT_HERSHEY_SIMPLEX, dimensiune de 0.5, de culoarea verde și grosimea de 2 pixeli
    #pentru a indica că acea linie verde semnifică axa Y
    cv2.putText(imagine_curentă, "Y", (int(centru_img_X - 15), int(centru_img_Y - 55)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    #pe imaginea curentă, se desenează un cerc albasatru, plin, de raza 5 (pixeli) în punctul (centru_img_X , centru_img_Y) pentru a ilustra care este axa Z pe imagine    
    cv2.circle(imagine_curentă, (int(centru_img_X), int(centru_img_Y)), 5, (255, 0, 0), -1)
    #pe imaginea curentă, se scrie un Z la punctul (centru_img_X+15 , centru_img_Y+25) cu fontul FONT_HERSHEY_SIMPLEX, dimensiune de 0.5, de culoarea albastră și grosimea de 2 pixeli
    #pentru a indica că acea linie albatră semnifică axa Z și oferă senzația că iese din imagine
    cv2.putText(imagine_curentă, "Z", (int(centru_img_X + 15), int(centru_img_Y + 25)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

#rezoluția camerei    
lungime_img = 1280      #lungimea imagini în funcție de numărul de pixeli
lățime_img = 720        #lățimea imagini în funcție de numărul de pixeli

fx = 1050  ################################################################################################### focal length in pixels
fy = 1050
centru_img_X = lungime_img / 2                                  #coordonata X a centrului imaginii, folosită pe mai departe ca și origine a celor 3 axe
centru_img_Y = lățime_img / 2                                   #coordonata Y a centrului imaginii, folosită pe mai departe ca și origine a celor 3 axe


pipeline = dai.Pipeline()                                       #creează un flux de procesare a imaginilor venite de la cameră

cameră_RGB = pipeline.createColorCamera()                       #adaugă o cameră RGB în pipeline, cu care se vor captura imagini color
cameră_RGB.setPreviewSize(lungime_img, lățime_img)              #se specifică dimensiunile (lungimea și lățimea) imaginii pe care camera o furnizează
cameră_RGB.setInterleaved(False)                                #se specifică ca fiecare canal de culoare (R, G, B) să fie stocat separat pentru o procesare mai ușoară
cameră_RGB.setFps(30)                                           #se specifică rata de imagini pe secundă (frames per second)

cameră_stereo = pipeline.create(dai.node.StereoDepth)                              #se adaugă o cameră stereo folosită, în final, pentru calcularea distanței
cameră_stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.DEFAULT)     #se setează parametrii camerei în modul implicit
cameră_stereo.setLeftRightCheck(True)                                              #este o filtrare a punctelor false, deoarece acesta verifică că obiectele sunt detectate de ambele camere
cameră_stereo.setExtendedDisparity(False)                                          #este setat pentru detecția cu o precizie mai bună a obiectelor mai departe de 75 cm față de cameră
cameră_stereo.setSubpixel(True)                                                    #folosit pentru îmbunătățirea preciziei

# Configure mono cameras
cameră_mono_stânga = pipeline.createMonoCamera()                                        #se adaugă camera mono din partea stângă
cameră_mono_dreapta = pipeline.createMonoCamera()                                       #se adaugă camera mono din partea dreapta
cameră_mono_stânga.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)   #setează rezoluția camerei din partea stângă, are o precizie medie și o viteză de procesare mare
cameră_mono_dreapta.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)  #setează rezoluția camerei din partea dreaptă
cameră_mono_stânga.setBoardSocket(dai.CameraBoardSocket.CAM_B)                          #se leagă la portul fizic al camerei, CAM_B = camera mono din stânga
cameră_mono_dreapta.setBoardSocket(dai.CameraBoardSocket.CAM_C)                         #se leagă la portul fizic al camerei, CAM_C = camera mono din dreapta

cameră_mono_stânga.out.link(cameră_stereo.left)                                         #se conectează ieșirea camerei mono din stânga la intrarea stângă a camerei stereo
cameră_mono_dreapta.out.link(cameră_stereo.right)                                       #se conectează ieșirea camerei mono din dreapta la intrarea dreaptă a camerei stereo

# Create outputs
xoutRgb = pipeline.createXLinkOut()
xoutRgb.setStreamName("rgb")
cameră_RGB.preview.link(xoutRgb.input)

xoutDepth = pipeline.createXLinkOut()
xoutDepth.setStreamName("depth")
cameră_stereo.depth.link(xoutDepth.input)

# Start the device
with dai.Device(pipeline) as device:
    # Get output queues
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    qDepth = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
    
    # Create window and set mouse callback
    cv2.namedWindow("Object Selection")
    cv2.setMouseCallback("Object Selection", draw_rectangle)
    
    # Processing loop
    while True:
        # Get frames
        inRgb = qRgb.get()
        inDepth = qDepth.get()
        
        # Convert to OpenCV format
        rgbFrame = inRgb.getCvFrame()
        depthFrame = inDepth.getFrame()
        
        # Convert to HSV for color tracking
        hsvFrame = cv2.cvtColor(rgbFrame, cv2.COLOR_BGR2HSV)
        
        # Draw the coordinate system origin
        draw_origin(rgbFrame, centru_img_X, centru_img_Y)
        
        # Clone frame for conturare_obiect
        clone = rgbFrame.copy()
        
        # Draw ROI selection rectangle if in progress
        if not obiect_selectat and conturare_obiect:
            cv2.rectangle(clone, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 2)
        
        # If color range is set, do object tracking
        if limita_inferioara_culoare is not None and limita_superioară_culoare is not None:
            # Create color mask
            mask = cv2.inRange(hsvFrame, limita_inferioara_culoare, limita_superioară_culoare)
            
            # Clean up mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            #cv2.imshow("mask", mask)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process contours to find the object
            if contours:
                # Find the largest contour (should be the object)
                c = max(contours, key=cv2.contourArea)
                
                # Only proceed if contour is large enough
                if cv2.contourArea(c) > 100:
                    # Get the bounding circle
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    x, y, radius = int(x), int(y), int(radius)
                    
                    # Draw circle around the object
                    cv2.circle(clone, (x, y), radius, (0, 255, 0), 2)
                    cv2.circle(clone, (x, y), 2, (0, 0, 255), -1)
                    
                    # Calculate corresponding point in depth map
                    depthX = int(x * depthFrame.shape[1] / rgbFrame.shape[1])
                    depthY = int(y * depthFrame.shape[0] / rgbFrame.shape[0])
                    
                    # Ensure coordinates are within bounds
                    depthX = max(0, min(depthX, depthFrame.shape[1] - 1))
                    depthY = max(0, min(depthY, depthFrame.shape[0] - 1))
                    
                    # Check depth around the point (5x5 region)
                    region_size = 5
                    xMin = max(0, depthX - region_size)
                    xMax = min(depthFrame.shape[1] - 1, depthX + region_size)
                    yMin = max(0, depthY - region_size)
                    yMax = min(depthFrame.shape[0] - 1, depthY + region_size)
                    
                    depthRegion = depthFrame[yMin:yMax, xMin:xMax]
                    
                    # Get non-zero depth values
                    nonZeroDepths = depthRegion[depthRegion > 0]
                    
                    if len(nonZeroDepths) > 0:
                        # Get median depth (more robust to outliers)
                        depth = np.median(nonZeroDepths)
                        
                        # Calculate 3D coordinates (in centimeters)
                        Z = depth / 10.0  # Convert to centimeters
                        X = (x - centru_img_X) * Z / fx
                        Y = (y - centru_img_Y) * Z / fy
                        
                        # Display 3D position in centimeters
                        text = f"Position: X={X:.1f}cm, Y={Y:.1f}cm, Z={Z:.1f}cm"
                        write_distance_to_file(X, Y)
                        cv2.putText(clone, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.7, (0, 255, 0), 2)
                    
                        # Draw a line from origin to object position
                        cv2.line(clone, (int(centru_img_X), int(centru_img_Y)), (x, y), (255, 165, 0), 2)
        
        # Show the frame
        cv2.imshow("Object Selection", clone)
        
        # Exit on 'q' or ESC key
        key = cv2.waitKey(1)
        if key == 27 or key == ord('q'):  # ESC or 'q'
            break
        elif key == ord('r'):  # 'r' to reset ROI selection
            obiect_selectat = False
            limita_inferioara_culoare = None
            limita_superioară_culoare = None
            print("Reset ROI selection. Select new object.")

cv2.destroyAllWindows()