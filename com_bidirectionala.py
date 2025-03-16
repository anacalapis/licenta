from bluetooth import *
import serial
import threading
import time
from datetime import datetime, timedelta

lock = threading.Lock()

buf_size = 1024

# Adresele ESP32
addr_esp1 = "A0:A3:B3:97:55:46" #fluier
addr_esp2 = "A0:A3:B3:96:69:6A" #inel
addr_esp3 = "CC:DB:A7:98:C1:8A" #imu

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
	    
def just_rx_and_echo(sock):
    while True:
	#with lock:
        data = sock.recv(buf_size)
        if data:
            data = data.decode("utf-8")
            print(f"IMU {data}")
            #formatted_data = f"{identifier}{data}\n"
            #ser.write(formatted_data.encode("utf-8"))	  
	      
def imu_camera(sock_imu, sock_inel, identifier):
    while True:
        max_samples = 50
        vector_imu = [0] * max_samples
        vector_camera= [0] *  max_samples
        i=0
       
        start_timp = datetime.now()
        while datetime.now() < start_timp + timedelta(seconds=2) and i < max_samples:
            data_imu = sock_imu.recv(buf_size).decode("utf-8")	#vin sub forma de string
            if data_imu != 0:
                vector_imu[i] = float(data_imu)
                with lock:
                    with open("distanta.txt", "r") as file:
                        continut = file.read()
                        if continut:
                            vector_camera[i] = float(continut)
                i += 1
            #i += 1
            time.sleep(0.05)
        maxim = 0
        index=0
        for j in range(i):
            if vector_imu[j] > maxim:
                maxim = vector_imu[j]
                index = j
            print(f"{vector_imu[j]}->{vector_camera[j]}")
        formatted_data = f"{identifier}{vector_camera[index]}\n"
        sock_inel.send(formatted_data.encode('utf-8'))
	
	    
def input_and_send(sock, identifier):
    while True:
        with lock:
            data = ser.readline().decode('utf-8').strip()
	    #print(data)
            if data == "S" or data == "P" or data == "L":
		#print(data)
                formatted_data = f"{identifier}{data}\n"
                sock.send(formatted_data.encode('utf-8'))
		#sock.send("\n".encode('utf-8'))
                ser.flush()  # Asigură-te că buffer-ul serial este golit

def read_and_transmit_distance(sock, identifier):
    while True:
        with lock:
            with open("distanta.txt", "r") as file:
                continut = file.read()
                if continut:
                    #print(continut)
                    formatted_data = f"{identifier}{continut}\n"
                    sock.send(formatted_data.encode('utf-8'))
                    #sock.send("\n".encode('utf-8'))
	
	
# Conectare la ESP32-urile
sock1 = connect_to_esp(addr_esp1) #fluier
sock2 = connect_to_esp(addr_esp2) #inel
sock3 = connect_to_esp(addr_esp3) #imu

# Asigură-te că ambele conexiuni sunt valide
if sock1 is None or sock2 is None or sock3 is None:
    print("Failed to connect to ESP32 devices.")
    exit(1)


# Creează fire de execuție pentru fiecare ESP32
thread1 = threading.Thread(target=rx_and_echo, args=(sock1, 0))  # fluier
thread2 = threading.Thread(target=rx_and_echo, args=(sock2, 1))  # inel
thread3 = threading.Thread(target=input_and_send, args=(sock2,3))  # trimitere semnal pauza
thread4 = threading.Thread(target=just_rx_and_echo, args=(sock3, ))  # vedem ce iese de la imu
thread5 = threading.Thread(target=imu_camera, args=(sock3, sock2, 4))	#datele de la imu

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
