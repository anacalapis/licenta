import depthai as dai
import cv2
import numpy as np
import math
import threading 

#variabilele de mai jos sunt explicate în funcția de mai jos, acolo unde sunt și folosite
conturare_obiect = False
coord_init_click_X, coord_init_click_Y = -1, -1
colț_stânga_sus_X, colț_stânga_sus_Y, lung_chenar, lățime_chenar = 0, 0, 0, 0
obiect_selectat = False
limita_inferioara_culoare = None
limita_superioară_culoare = None

lock = threading.Lock()                                 #crează un obiect de tip ”lock” care este folosit pentru a limita accesul la o resursa ce poate fi accesată de mai multe fire de execuție   
            
def scrie_distanță_în_fișier(X, Y):                     #funcție care este responsabilă de scrierea într-un fișier al unui mesaj 
                                                        #de forma A„distanța_până_la_inelul1”B„distanța_până_la_inelul2”
    with lock:                                          #pentru a nu permite altui fir de execuție să efectueze operații asupra fișierului
        with open("distanta.txt", "w") as file:         #fișierul este deschis pentru scriere și se va face referire la acesta prin variabila ”file”
            
            #se calculează distanța față de ambele panouri
            #coordonatele inelelor au fost obținute tot cu ajutorul camerei, pentru o precizie mai exactă
            #datorită faptului că originea camerei față de care se calculează nu este chiar la centru terenului din vina suportului
            distanță_inel_A = math.sqrt((X + 68.5)**2 + (Y +6)**2)                                          #coordonata inelului A (-68.5,-6)
            distanță_inel_B = math.sqrt((X - 70)**2 + (Y -9.5)**2)                                          #coordonata inelului B (70, 9.5)
          
            file.write(f'A{round(distanță_inel_A,3)}B{round(distanță_inel_B,3)}')                           #scriere în fișier după șablonul dorit
            distanță_inel_A = f"{round(distanță_inel_A,3)}"                                                 #am transformat distanțele în șiruri de caractere pentru a putea fi printate pe ecran
            distanță_inel_B = f"{round(distanță_inel_B,3)}"                         
            
            cv2.putText(clonă, distanță_inel_A, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)   #pentru a știi distanțele ce sunt scrise în fișier
            cv2.putText(clonă, distanță_inel_B, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)   #le-am printat și pe ecran

def desenare_chenar_culoare(event, x, y, flags, param):                          #funcție specifică OpenCV care monitorizează evenimentele mouse-ului
                                                                                 #x, y reprezintă coordonatele curente ale mouse-ului
    global coord_init_click_X, coord_init_click_Y                                #coordonatele inițiale în momentul în care se apasă pe mouse pt a începe selecția
    global conturare_obiect                                                      #este de tip boolean și indică dacă se desenează conturul, în acel moment
    global obiect_selectat                                                       #devine adevărată atunci când s-a selectat o bucată din imagine
    global colț_stânga_sus_X, colț_stânga_sus_Y                                  #coordonatele colțului din stânga sus
    global lung_chenar, lățime_chenar                                            #lățimea și lungimea dreptunghiului
    global limita_inferioara_culoare, limita_superioară_culoare                  #limita inferioară și superioară al intervalului de valori a culorii selectate în HSV
    if event == cv2.EVENT_LBUTTONDOWN:                                           #când este apăsat butonul stâng al mouse-ului, înseamnă că începe selectarea obiectului
        conturare_obiect = True                                                  #se pune variabila pe adevărat
        coord_init_click_X, coord_init_click_Y = x, y                            #se salvează coordonatele unde s-a dat click prima dată pe imagine pentru a începe selecția
    elif event == cv2.EVENT_MOUSEMOVE:                                           #dacă mouse-ul se mișcă și s-a început selecția
        if conturare_obiect:                                                     #indică începutul selecții
            colț_stânga_sus_X, colț_stânga_sus_Y = min(coord_init_click_X, x), min(coord_init_click_Y, y)      #se actualizează în permanență coordonatele colțului din stânga-sus
            lung_chenar, lățime_chenar = abs(coord_init_click_X - x), abs(coord_init_click_Y - y)    #se actualizează în permanență lungimea și lățimea dreptunghiului ce urmează să se formeze
    elif event == cv2.EVENT_LBUTTONUP:                                           #dacă nu se mai ține butonul stâng apăsat, înseamnă că selecția obiectului s-a terminat
        conturare_obiect = False                                                 #indică terminarea efectuării conturului
        obiect_selectat = True                                                   #indică existența unei zone deja selectate (regiune de interes)
        roi = cadru_HSV[colț_stânga_sus_Y:colț_stânga_sus_Y+lățime_chenar, colț_stânga_sus_X:colț_stânga_sus_X+lung_chenar]      #se extrage zona selectată, în format HSV  
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

def desenare_axe(imagine_curentă, centru_img_X, centru_img_Y):
       
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
lungime_img = 1280                                                                  #lungimea imagini în funcție de numărul de pixeli
lățime_img = 720                                                                    #lățimea imagini în funcție de numărul de pixeli

fx = 1050                                                                           #distanța focală în pixeli
fy = 1050
centru_img_X = lungime_img / 2                                                      #coordonata X a centrului imaginii, folosită pe mai departe ca și origine a celor 3 axe
centru_img_Y = lățime_img / 2                                                       #coordonata Y a centrului imaginii, folosită pe mai departe ca și origine a celor 3 axe


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

cameră_mono_stânga = pipeline.createMonoCamera()                                        #se adaugă camera mono din partea stângă
cameră_mono_dreapta = pipeline.createMonoCamera()                                       #se adaugă camera mono din partea dreapta
cameră_mono_stânga.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)   #setează rezoluția camerei din partea stângă, are o precizie medie și o viteză de procesare mare
cameră_mono_dreapta.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)  #setează rezoluția camerei din partea dreaptă la 640x400
cameră_mono_stânga.setBoardSocket(dai.CameraBoardSocket.CAM_B)                          #se leagă la portul fizic al camerei, CAM_B = camera mono din stânga
cameră_mono_dreapta.setBoardSocket(dai.CameraBoardSocket.CAM_C)                         #se leagă la portul fizic al camerei, CAM_C = camera mono din dreapta

cameră_mono_stânga.out.link(cameră_stereo.left)                                         #se conectează ieșirea camerei mono din stânga la intrarea stângă a camerei stereo
cameră_mono_dreapta.out.link(cameră_stereo.right)                                       #se conectează ieșirea camerei mono din dreapta la intrarea dreaptă a camerei stereo

out_RGB = pipeline.createXLinkOut()                                                     #creează un nod ce va transmite datele prin USB către Raspberry și va fi folosit pentru imaginea RGB
out_RGB.setStreamName("RGB")                                                            #se setează numele fluxului de date ce se ocupă de transmiterea imaginii RGB                                 
cameră_RGB.preview.link(out_RGB.input)                                                  #se leagă la intrarea fluxului de date, camera RGB, definită anterior

out_adâncime = pipeline.createXLinkOut()                                                #se creează un alt nod ce va fi folosit pentru adâncime
out_adâncime.setStreamName("adâncime")                                                  #se seteaza numele fluxului de date ce va fi responsabil de adâncime
cameră_stereo.depth.link(out_adâncime.input)                                            #se leagă la intrarea fluxului de date, camera stereo (folosită pt adâncime), definită anterior

with dai.Device(pipeline) as device:                                                    #creează conexiunea între program și camera OAK-D Lite printr-un pipeline
                                                                                        #se pornește camera
    coadă_RGB = device.getOutputQueue(name="RGB", maxSize=4, blocking=False)            #creează o coadă, de 4 cadre, în care se stochează cadrele RGB
    coadă_adâncime = device.getOutputQueue(name="adâncime", maxSize=4, blocking=False)  #creează o coadă, de 4 cadre, în care se stochează harta de adâncime
    #parametrul blocking este setat pe False pentru ca în cazul în care nu există cadru disponibil în coada de așteptare, programul să nu se blocheze, ci să returneze un None ce poate fi gestionat

    cv2.namedWindow("Imagine cameră")                                                   #se dă nume ferestrei ce urmează să fie afișată pe ecran
    cv2.setMouseCallback("Imagine cameră", desenare_chenar_culoare)                     #leagă funcția ce se ocupă de mișcările mouse-ului, la fereastra dată

    while True:
        cadru_RGB = coadă_RGB.get()                                                     #se ia un cadru din coada de așteptare pentru cadrele ce oferă imagini RGB
        cadru_adâncime = coadă_adâncime.get()                                           #se ia un cadru din coada de așteptare a hărții de adâncime
        
        cadru_BGR = cadru_RGB.getCvFrame()                                              #se obține un cadru compatibil cu OpenCV, imaginea RGB este transformată în BGR
        matrice_adâncime = cadru_adâncime.getFrame()                                    #se extrage doar imaginea de adâncime, sub formă de matrice 2D

        cadru_HSV = cv2.cvtColor(cadru_BGR, cv2.COLOR_BGR2HSV)                          #transformă din format BGR în format HSV, folosit pentru detecția culorii
     
        desenare_axe(cadru_BGR, centru_img_X, centru_img_Y)                             #se apelează funcția care desenează axele de coordonate peste iamgine
  
        clonă = cadru_BGR.copy()                                                        #se face o copie a imaginii originale, pentru a lucra pe o copie, nu pe original
        
        if not obiect_selectat and conturare_obiect:                                    #dacă nu avem un obiect selectat, dar suntem în procesul de selectare
            cv2.rectangle(clonă, (colț_stânga_sus_X, colț_stânga_sus_Y), (colț_stânga_sus_X + lung_chenar, colț_stânga_sus_Y + lățime_chenar), (0, 255, 0), 2)
            #se desenează, pe imaginea clonă, chenarul de culoare verde, de grosime 2, ce este desenat în timp real de utilizator, pentru a ce zonă selectează
        
        if limita_inferioara_culoare is not None and limita_superioară_culoare is not None:         #dacă există selectată o zonă din imagine, 
                                                                                                    #se formează automat intervalul de culoare în care se caută
            img_alb_negru = cv2.inRange(cadru_HSV, limita_inferioara_culoare, limita_superioară_culoare)     #se creează o imagine alb-negru, unde pixeli ce se află în acel interval
                                                                                                    #devin albi, iar ceilalți devin negri
            matrice = np.ones((5, 5), np.uint8)                                                     #definirea matricei folosită la operații de curățare a imaginii
            img_alb_negru = cv2.morphologyEx(img_alb_negru, cv2.MORPH_OPEN, matrice)                #elimină petele albe mici și izolate
            img_alb_negru = cv2.morphologyEx(img_alb_negru, cv2.MORPH_CLOSE, matrice)               #face obiectele detectate mai clare prin astuparea micilor pete negre de pe suprafețele albe            
        
            contururi, _ = cv2.findContours(img_alb_negru, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #detectează contururile albe din imagine
        
            if contururi:                                                               #daca există lista de contururi
                contur = max(contururi, key=cv2.contourArea)                            #alege cel mai mare contur din imagine, unde cv2.contourArea calculează suprafața obiectului detectat

                if cv2.contourArea(contur) > 100:                                       #dacă conturul este suficient de mare, eu l-am luat 100 de pixeli
                    ((x, y), rază) = cv2.minEnclosingCircle(contur)                     #caută cel mai mic contur care înconjoară obiectul
                    x, y, rază = int(x), int(y), int(rază)                              #pe baza conturului găsit, se extrage centrul cercului și raza acestuia
                    
                    cv2.circle(clonă, (x, y), rază, (0, 255, 0), 2)                     #se desenează conturul cercului găsit, cu culoarea verde și o grosime de 2 pixeli
                    cv2.circle(clonă, (x, y), 2, (0, 0, 255), -1)                       #se pune un punct în centrul cercului
                                                                
                    #pentru că imaginea RGB și imaginea cu valorile de adâncime au rezoluții diferite, se face următorul calcul 
                    #pentru a cunoaște corespondentul coordonatelor centrului cercului din imaginea BGR, în imaginea de adâncime (pentru a afla adâncimea acestui punct)
                    pct_adâncime_X = int(x * matrice_adâncime.shape[1] / cadru_BGR.shape[1])    #coordonata X a punctului corespondent în imaginea de adâncime; .shape[1]- lățimea imaginii
                    pct_adâncime_Y = int(y * matrice_adâncime.shape[0] / cadru_BGR.shape[0])    #coordonata Y a punctului corespondent în imaginea de adâncime; .shape[0]- lungimea imaginii
                    
                    pct_adâncime_X = max(0, min(pct_adâncime_X, matrice_adâncime.shape[1] - 1)) #verificăm noile coordonate pentru a nu ieși din imaginea de adâncime
                    pct_adâncime_Y = max(0, min(pct_adâncime_Y, matrice_adâncime.shape[0] - 1))
                
                    zonă = 5                                                            #lungimea pătratului care este folosit pentru a analiza adâncimea
                                                                                        #nu ne uitâm doar în centrul cercului, ci pe o zonă de 5x5 pixeli, pentru a oferi o stabiliate mai mare
                    #se definesc colțurile pătratului ce se formează în jurul centrului cercului
                    xMin = max(0, pct_adâncime_X - zonă)                                #ne asigurăm că nu mergem prea în stânga
                    xMax = min(matrice_adâncime.shape[1] - 1, pct_adâncime_X + zonă)    #ne asigurăm că nu mergem prea în dreapta
                    yMin = max(0, pct_adâncime_Y - zonă)                                #ne asigurăm că nu mergem prea sus
                    yMax = min(matrice_adâncime.shape[0] - 1, pct_adâncime_Y + zonă)    #ne asigurăm că nu mergem prea jos
                    
                    regiune_adâncime = matrice_adâncime[yMin:yMax, xMin:xMax]           #se extrage zona de adâncime a pătratului definit mai sus
                    
                    regiune_adâncime_corect = regiune_adâncime[regiune_adâncime > 0]    #păstrează distanțele corecte, cele care au 0 înseamnă că nu au nicio dată
                    
                    if len(regiune_adâncime_corect) > 0:                                #dacă există astfel de date
                        adâncime_out = np.median(regiune_adâncime_corect)               #calculează mediana din acea regiune și NU media valorilor
                                                                                        #mediana = valoarea din mijloc care oferă o estimare mai sigură
                        
                        Z = adâncime_out / 10.0                                         #convertește valorea distanței în centimetri
                        X = (x - centru_img_X) * Z / fx                                 #diferența față de centru este înmulțit cu adâncimea obținută și apoi împărțit la focal length
                        Y = (y - centru_img_Y) * Z / fy
                        
                        scrie_distanță_în_fișier(X, Y)                                                      #coordonatele punctului sunt transmise ca și parametru pt a se calcula distanța până la inele

                        text = f"Coordonatele centrului mingii: X={X:.1f}cm, Y={Y:.1f}cm, Z={Z:.1f}cm"      #se formează un string ce urmează sa fie scrie pe imagine
                        cv2.putText(clonă, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)   #este scris pe imagine
        
        cv2.imshow("Imagine cameră", clonă)                       #afișarea imaginii după toate operațiile și calculele făcute
        
        tasta = cv2.waitKey(1)                                    #se așteapta ca o tastă să fie apăsată
        if tasta == ord('q'):                                     #dacă se apasă q, atunci programul se va încheia
            break
        elif tasta == ord('r'):                                   #dacă se apasă r, se face o reselectare a obiectului pentru a extrage culoarea pe care dorim să o urmărim
            obiect_selectat = False
            limita_inferioara_culoare = None
            limita_superioară_culoare = None
            print("Reselectarea obiectului.")

cv2.destroyAllWindows()