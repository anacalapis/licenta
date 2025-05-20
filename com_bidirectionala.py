from bluetooth import *
import serial
import threading
import time
from datetime import datetime, timedelta

lock = threading.Lock()

buf_size = 1024

buffer_size = 5
vector_camera = [0] * buffer_size
vector_imu = [0] * buffer_size

# Adresele ESP32
addr_esp1 = "A0:A3:B3:97:55:46" #fluier
addr_esp2 = "A0:A3:B3:96:69:6A" #inel1
addr_esp3 = "A0:A3:B3:97:4A:56" #imu
addr_esp4 = "D4:8A:FC:A2:70:5A" #inel2

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# Funcție pentru conectarea unui dispozitiv
def connect_to_esp(addr):
    service_matches = find_service(address=addr)
    if len(service_matches) == 0:
        print(f"Couldn't find the SampleServer service for {addr} =(")
        return None

    first_match = service_matches[0]
    port = first_match["port"]
    host = first_match["host"]

    sock = BluetoothSocket(RFCOMM)
    sock.connect((host, port))
    print(f"Connected to {addr}")
    return sock

# Funcție pentru recepția datelor de la un ESP32
def rx_and_echo(sock, identifier):
    while True:
	#with lock:
        data = sock.recv(buf_size)
        if data:
            data = data.decode("utf-8")
            #print(f"{identifier}{data}")
            formatted_data = f"{identifier}{data}\n"
            ser.write(formatted_data.encode("utf-8"))
	     
	      
def imu_camera(sock_imu, sock_inelA, sock_inelB, identifier):
    start_timp = datetime.now()
    i=0
    while True:
        if (datetime.now() - start_timp).seconds <1:
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
            
            formatted_data = f"{identifier}{vector_camera[index]}\n"
            print(f"TRANSM {formatted_data}")
            sock_inelA.send(formatted_data.encode('utf-8'))
            sock_inelB.send(formatted_data.encode('utf-8'))
            i=0
            start_timp = datetime.now() 
	    
def input_and_send(sock1, sock2, identifier):
    while True:
        with lock:
            data = ser.readline().decode('utf-8').strip()
            #print(data)
            if data == "S" or data == "P" or data == "L" or data == "A" or data == "B" or data == "a" or data == "b" or data.startswith("H"):
                #print(data)
                formatted_data = f"{identifier}{data}\n"
                sock1.send(formatted_data.encode('utf-8'))
                sock2.send(formatted_data.encode('utf-8'))
		#sock.send("\n".encode('utf-8'))
                ser.flush()  # Asigură-te că buffer-ul serial este golit
	
# Conectare la ESP32-urile
sock1 = connect_to_esp(addr_esp1) #fluier
sock2 = connect_to_esp(addr_esp2) #inel1
sock3 = connect_to_esp(addr_esp3) #imu
sock4 = connect_to_esp(addr_esp4) #inel2

sock2.send("RESET")
sock4.send("RESET")

# Asigură-te că ambele conexiuni sunt valide
if sock1 is None or sock2 is None or sock4 is None: # or sock4 is None:
    print("Failed to connect to ESP32 devices.")
    exit(1)

# Creează fire de execuție pentru fiecare ESP32
thread1 = threading.Thread(target=rx_and_echo, args=(sock1, 0))  # fluier
thread2 = threading.Thread(target=rx_and_echo, args=(sock2, 1))  # inel
thread3 = threading.Thread(target=input_and_send, args=(sock2, sock4,3))  # trimitere semnal pauza
thread4 = threading.Thread(target=rx_and_echo, args=(sock4, 2))     #trimitem datele de la inel2 la arduino 
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