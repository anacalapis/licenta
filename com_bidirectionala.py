from bluetooth import *				#find_service 
import serial
import threading
import time
from datetime import datetime, timedelta

lock = threading.Lock()

buf_size = 1024

buffer_size = 10
vector_camera = [0] * buffer_size			#vectorul responsabil care memoreaza distanta pe parcursul intervalului de o secunda
vector_imu = [0] * buffer_size				#vector care memoreaza datele venite de la IMU pe parcursul unei secunde, iar la final, se va trimite valoarea distantei aferenta celei mai mari valori inregistrate in acest vector

adresa_ESP1 = "A0:A3:B3:97:55:46" #fluier			#adresa MAC a ESP-ului ce gestioneaza fluierul si cele 2 butoane
adresa_ESP2 = "A0:A3:B3:96:69:6A" #inel1			#adresa MAC a ESP-ului ce este pozitionat pe inelul 1
adresa_ESP3 = "A0:A3:B3:97:4A:56" #imu			    #adresa MAC a ESP-ului ce este introdus in minge si primeste date de la IMU
adresa_ESP4 = "D4:8A:FC:A2:70:5A" #inel2			#adresa MAC a ESP-ului ce este pozitionat pe inelul 2

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)		#creeaza o conexiune seriala la portul "/dev/ttyACM0", cu o rata de transmitere a datelor de 9600 biti pe secunda	


def conectare_la_ESP(adresa_MAC):						#funcție ce este folosita pentru conectarea unui ESP prin protocolul Bluetooth
    dict_servicii = find_service(address=adresa_MAC)			#functia find_service, din PyBluez, cauta daca exista servicii Bluetooth pe dispozitivul dat ca paramteru, prin intermediul adresei MAC
									#aceasta functie returneaza o lista de dictionare, unde fiecare dictionar reprezinta o pereche cheie-valoare cu diferite servicii ce sunt oferite de dispozitivul respectiv
    if len(dict_servicii) == 0:					#daca nu este gasit niciun serviciu, atunci inseamna ca nu s-a realizat conexiunea si se da un mesaj de eroare
        print(f"Nu s-a putut gasi dispozitivul cu adresa MAC {adresa_MAC}")
        return None

    primul_serviciu = dict_servicii[0]					#se alege primul serviciu din lista
    port = primul_serviciu["port"]						#se extrage informatia legata de port
    host = primul_serviciu["host"]						#se extrage informatia legata de adresa IP la care dispozitivul se va conecta

    sock = BluetoothSocket(RFCOMM)					#creeaza un obiect care permite realizarea unei conexiuni Bluetooth intre 2 dispozitive
    sock.connect((host, port))						#stabileste conexiunea dintre RaspberryPi si dispozitiv, prin adresa IP si portul acestia
    print(f"Conectat la {adresa_MAC}")					#un mesaj care apare atunci cand conexiunea a fost stabilita
    return sock								#se returneaza un socket, ce urmeaza sa fie utilizat mai departe pentru a face referire la ESP 

# Funcție pentru recepția datelor de la un ESP32
def receptie_Bluetooth(sock, identificator):		#functie pentru receptia datelor, prin Bluetooth, de la un ESP si trimiterea lor mai departe prin interfata seriala
    while True:
        date_de_la_ESP = sock.recv(buf_size)			#se salveaza in variabila "date_de_la_ESP", mesajele ce vin prin Bluetooth de la ESP-ul prin socketul acestui
        if date_de_la_ESP:					#daca exista date venite
            date_de_la_ESP = data.decode("utf-8")			#datele sunt convertite din bytes, in string, pentru a putea fi interpretate
            date_de_la_ESP_formatate = f"{identificator}{date_de_la_ESP}\n"	#mesajul este formatat pentru a stii pe mai departe, de la ce ESP au venit datele
            ser.write(date_de_la_ESP_formatate.encode("utf-8"))	#mesajul formatat este transmis catre Arduino, prin intermediul interfetei seriale. Acest mesaj este convertit inapoi in bytes.
	     
	      
def imu_camera(sock_imu, sock_inelA, sock_inelB, identificator):    #corelarea informațiile ce vin de la IMU cu distanța măsurată de cameră
    timp_start = datetime.now() 
    i=0
    while True:
        if (datetime.now() - timp_start).seconds <1:
            data_imu = sock_imu.recv(buf_size).decode('utf-8').strip()	#vin sub forma de string
            if data_imu:
                vector_imu[i] = data_imu
                with open("distanta.txt", "r") as file:
                        continut = file.read()
                        if continut:
                            vector_camera[i] = continut
                            print(f"{vector_imu[i]}->{vector_camera[i]}")
                            i+=1
        else:
            val_max= 0
            index=0
            for x in range(i):
                if int(vector_imu[x]) > int(val_max):
                    val_max=vector_imu[x]
                    index=x
            #print(f"FFFFF {vector_imu[index]}->{vector_camera[index]}")
            
            formatted_data = f"{identificator}{vector_camera[index]}\n"
            print(f"TRANSM {formatted_data}")
            sock_inelA.send(formatted_data.encode('utf-8'))
            sock_inelB.send(formatted_data.encode('utf-8'))
            i=0
            timp_start = datetime.now() 
	    
def input_and_send(sock1, sock2, identificator):
    while True:
        with lock:
            data = ser.readline().decode('utf-8').strip()
            #print(data)
            if data == "S" or data == "P" or data == "L" or data == "A" or data == "B" or data == "a" or data == "b" or data.startswith("H"):
                #print(data)
                formatted_data = f"{identificator}{data}\n"
                sock1.send(formatted_data.encode('utf-8'))
                sock2.send(formatted_data.encode('utf-8'))
		#sock.send("\n".encode('utf-8'))
                ser.flush()  # Asigură-te că buffer-ul serial este golit
	
# Conectare la ESP32-urile
sock1 = conectare_la_ESP(adresa_ESP1) #fluier
sock2 = conectare_la_ESP(adresa_ESP2) #inel1
sock3 = conectare_la_ESP(adresa_ESP3) #imu
sock4 = conectare_la_ESP(adresa_ESP4) #inel2

sock2.send("RESET")
sock4.send("RESET")

# Asigură-te că ambele conexiuni sunt valide
if sock1 is None or sock2 is None or sock4 is None: # or sock4 is None:
    print("Failed to connect to ESP32 devices.")
    exit(1)

# Creează fire de execuție pentru fiecare ESP32
thread1 = threading.Thread(target=receptie_Bluetooth, args=(sock1, 0))  # fluier
thread2 = threading.Thread(target=receptie_Bluetooth, args=(sock2, 1))  # inel
thread3 = threading.Thread(target=input_and_send, args=(sock2, sock4,3))  # trimitere semnal pauza
thread4 = threading.Thread(target=receptie_Bluetooth, args=(sock4, 2))     #trimitem datele de la inel2 la arduino 
thread5 = threading.Thread(target=imu_camera, args=(sock3, sock2, sock4, 4))	#datele de la imu

thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()

# Așteaptă terminarea firelor
thread1.join()
thread2.join()
thread3.join()
thread4.join()
thread5.join()

# Închide conexiunile
sock1.close()
sock2.close()
sock3.close()
sock4.close()





#documentatie https://pybluez.readthedocs.io/en/latest/api/find_service.html