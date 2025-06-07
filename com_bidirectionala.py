from bluetooth import *                              #bibliotecă folosită pentru comunicarea Bluetooth
import serial                                        #pentru a comunica pe porturile seriale (placa Arduino)
import threading                                     #permite execuția mai multor funcții, în paralel
from datetime import datetime                        #pentru a accesa data și ora curentă 
import os                                            #folosit pentru operații de sistem 

lock = threading.Lock()                              #crează un „lacăt” pentru a nu permite ca o resursă să fie accesată, în același timp, de mai multe fire de execuție

buf_size = 1024                                      #numărul maxim de bytes care pot fi recepționați, la o singură citire, de un socket
buffer_size = 10                                     #lungimea maximă a celor 2 vectori definiți mai jos
vector_camera = [0] * buffer_size                    #vector folosit pentru salvarea datelor ce vin de la modul MPU6050
vector_imu = [0] * buffer_size                       #vector folosit pentru salvarea mesajului ce conține distanțele până la cele 2 inele

adresa_ESP1 = "A0:A3:B3:97:55:46"                    #adresa MAC a ESP-ului ce se ocupă de procesarea datelor de la modulul ce se ocupă de pornirea/oprirea timpului și ștergerea ultimului coș
adresa_ESP2 = "A0:A3:B3:96:69:6A"                    #adresa MAC a ESP-ului ce se ocupă de gestionarea punctelor marcate la inelul 1
adresa_ESP3 = "A0:A3:B3:97:4A:56"                    #adresa MAC a ESP-ului ce se ocupă de găsirea momentului în care mingea părăsește mâna, cu ajutoul modulului MPU6050
adresa_ESP4 = "D4:8A:FC:A2:70:5A"                    #adresa MAC a ESP-ului ce se ocupă de gestionarea punctelor marcate la inelul 1

porturi_seriale_posibile=['/dev/ttyACM0', '/dev/ttyACM1']   #cele 2 porturi seriale la care poate fi conectată placa Arduino
port_serial= None                                           #inițierea variabilei ce va conține obiectul de conexiune serială
for port in porturi_seriale_posibile:                       #se caută în lista porturilor posibile
    if os.path.exists(port):                                #se verifcă dacă există 
        port_serial = serial.Serial(port,9600, timeout=1)   #se realizează conexiunea serială cu portul găsit, la o frecvență de 9600 biți/secundă
        break

def conectare_la_ESP(addr):                                 #funcția ce se ocupă de conectarea prin Bluetooth la un ESP32, ce este dat prin adresa MAC ca și argument
    servicii = find_service(address=addr)                   #se caută dacă există servicii Bluetooth 
    if len(servicii) == 0:                                  #dacă nu există niciun serviciu
        print(f"Nu s-a gasit ESP-ul cu adresa {addr} =(")   #se afișează un mesaj de eroare
        return None

    primul_serviciu = servicii[0]                           #se extrage primul serviciu
    port = primul_serviciu["port"]                          #se extrage portul bluetooth RFCOMM la care trebuie să ne conectăm
    host = primul_serviciu["host"]                          #se extrage adresa MAC a dispozitivului     

    sock = BluetoothSocket(RFCOMM)                          #crează un socket pe protocolul RFCOMM
    sock.connect((host, port))                              #se conectează la adresa și portul obținute mai sus a dispozitivului ESP32
    print(f"Conectat la {addr}")                            #se afișează un mesaj de succes
    return sock                                             #se returnează socket-ul

def pune_date_pe_serial(sock, identificator):               #este o funcție care primește date de la un ESP32 si le scrie pe serial către Arduino
    while True:
        with lock: ##aici l am pus sa vad daca totul e ok
            data = sock.recv(buf_size)                          #recepționează datele de la socket
            if data:                                            #dacă există date
                data = data.decode("utf-8")                     #le decodifică într-un format citibil, sub forma șirurilor de caracter
                date_formatate = f"{identificator}{data}\n"     #se formatează mesajul, se adaugă în fața lui un identificator, pentru a știi pe mai departe de la ce dispozitiv este mesajul
                port_serial.write(date_formatate.encode("utf-8")) #se codifică mesajul înapoi în bytes pentru a putea fi trimis pe serial
	     
def imu_camera(sock_imu, sock_inelA, sock_inelB, identificator): #funcția ce face legătura dintre momentul de lansarea a mingii și distanța din fișierul text
    start_timp = datetime.now()                             #pentru a nu trimite prea multe date către inele, am ales să le mai filtrez și să trimit un mesaj/secundă
    i=0                                                     #indexul celor 2 vectori cu ajutorul cărora fac asocierea
    while True:
        if (datetime.now() - start_timp).seconds <1:        #dacă nu a trecut o secundă de la ultima trimitere, prelucrez datele
            data_imu = sock_imu.recv(buf_size).decode('utf-8').strip()	#iau datele de la modulul MPU6050, într-un format interpretabil și elimin toate spațiile
            if data_imu:                                    #dacă există date
                linii_imu= data_imu.splitlines()            #le împarte pe linii (aveam cazuri când mesaajul meu era compus din mai multe date separate prin \n)
                for linie in linii_imu:                     #se ia fiecare linie pentru a se asocia 
                    vector_imu[i] = linie                   #se salvează în vectorul destinat datelor ce vin de la MPU6050
                    with open("distanta.txt", "r") as file: #se deschide fișierul pentru a se citi datele
                            continut = file.read()          #se salvează datele citite într-o variabilă
                            if continut:
                                vector_camera[i] = continut #dacă există, se pun în vectorul dedicat distanțelor
                                #print(f"{vector_imu[i]}->{vector_camera[i]}")
                                i+=1                        #se incrementează indicele
        else:                                               #dacă a trecut mai mult de o secundă de când nu s-au trimis date
            val_max= 0                                      #se va căuta valoarea maximă trimisă de modulul MPU6050
            index=0                                         #si se va face corelarea cu distanța de pe acel index
            for x in range(i):                              #se parcurg toate valorile toate valorile venite de la MPU6050
                if int(vector_imu[x].strip()) > int(val_max): #pentru a se găsi valoarea maximă
                    val_max=vector_imu[x]
                    index=x                                 #se salvează indexul pentru a trimite distanța măsurată de la acel moment
            date_formatate = f"{identificator}{vector_camera[index]}\n" #se formatează mesajul pentru a știi de unde provine
            #print(f"TRANSM {date_formatate}")
            sock_inelA.send(date_formatate.encode('utf-8')) #se trimite mesajul formatat către primul inel
            sock_inelB.send(date_formatate.encode('utf-8')) #se trimite mesajul formatat către al doilea inel
            i=0                                             #se resetează indexul pentru o nouă căutare
            start_timp = datetime.now()                     #se salvează timpul pentru a știi cât a trecut de la ultima trimitere de mesaj
	    
def transmitere_date_catre_ESP(sock1, sock2, identificator):#se trimit mesaje către cele 2 inele cu datele de pe serial
    while True:
        with lock:                                          #pentru a nu trimite simultan pe același port serial
            data = port_serial.readline().decode('utf-8').strip()   #se decodifică datele pentru a ne asigura că trimitem doar avem nevoie
            if data == "S" or data == "P" or data == "L" or data == "A" or data == "B" or data == "a" or data == "b" or data.startswith("H"):
                date_formatate = f"{identificator}{data}\n" #dacă data trimisă este una acceptată, mesajul se formatează pentru a știi de la cine provine și cum să fie interpretat
                sock1.send(date_formatate.encode('utf-8'))  #se trimit datele către primul inel
                sock2.send(date_formatate.encode('utf-8'))  #se trimit datele către cel de al doilea inel
                port_serial.flush()                         #se asigură că buffer-ul serial este golit
	
sock1 = conectare_la_ESP(adresa_ESP1)                       #se realizează conexiunea cu ESP32 ce se ocupă de pornirea/oprirea timpului și ștergerea din buton
sock2 = conectare_la_ESP(adresa_ESP2)                       #se realizează conexiunea cu ESP32 ce se ocupă de gestionarea punctelor marcate de inelul 1
sock3 = conectare_la_ESP(adresa_ESP3)                       #se realizează conexiunea cu ESP32 ce se ocupă de momentul în care mingea a părăsit mâna jucătorului
sock4 = conectare_la_ESP(adresa_ESP4)                       #se realizează conexiunea cu ESP32 ce se ocupă de gestionarea punctelor marcate de inelul 2

sock2.send("RESET")                                         #se trimite o comanda de reset către inelul 1 pentru a porni cu scorul din dou de pe 0
sock4.send("RESET")                                         #se trimite o comanda de reset către inelul 2 pentru a porni cu scorul din dou de pe 0

if sock1 is None or sock2 is None or sock3 is None or sock4 is None:    #verificăm dacă toate dispozitivele au fost conectate
    print("Nu s-au conectat toate dispozitivele ESP32.")                #în caz negativ, lăsăm un mesaj de eroare
    exit(1)

#se creează fire de execuție pentru fiecare ESP32   
thread1 = threading.Thread(target=pune_date_pe_serial, args=(sock1, 0))  #trimite datele ce vin de la fluier/butoane prin portul serial ca să ajungă la Arduino și să fie interpretate 
thread2 = threading.Thread(target=pune_date_pe_serial, args=(sock2, 1))  #trimite datele ce vin de la inelul 1 prin portul serial
thread3 = threading.Thread(target=transmitere_date_catre_ESP, args=(sock2, sock4,3))  # trimitere către cele 2 inele mesajele ce se emise de Arduino pt controlul punctelor
thread4 = threading.Thread(target=pune_date_pe_serial, args=(sock4, 2))  #trimite datele ce vin de la inelul 2 prin portul serial
thread5 = threading.Thread(target=imu_camera, args=(sock3, sock2, sock4, 4))	#datele de la modulul MPU6050 sunt corelate cu distanța luată în acel moment și se transmite mai departe 

#pornirea celor 5 fire de execuție
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()

#se așteaptă până când se termină execuția thread-urilor
thread1.join()
thread2.join()
thread3.join()
thread4.join()
thread5.join()

#se închid conexiunile 
sock1.close()
sock2.close()
sock3.close()
sock4.close()