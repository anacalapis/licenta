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

#data_imu = []
#data_camera = []
#global data_imu, data_camera

# Adresele ESP32
addr_esp1 = "A0:A3:B3:97:55:46" #fluier
addr_esp2 = "A0:A3:B3:96:69:6A" #inel
#addr_esp3 = "CC:DB:A7:98:C1:8A" #imu
#addr_esp3 = "D4:8A:FC:A2:45:4E"
addr_esp3 = "A0:A3:B3:97:4A:56"

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
    #global data_imu
    index_i =0
    while True:
	#with lock:
        data = sock.recv(buf_size)
        if data:
            data = data.decode("utf-8")
            #vector_imu[index_i % buffer_size]= data.decode("utf-8")
            #print(f"I {vector_imu[index_i % buffer_size]}")
            #index_i +=1
            timp = datetime.now().strftime("%H:%M:%S.%f")
            #print(f"IMUUUU {timp} - {data}")
            data_imu.append((timp, data))
            #print(f"IMUUUU {timp} - {data}")
            #formatted_data = f"{identifier}{data}\n"
            #ser.write(formatted_data.encode("utf-8"))	  
	      
def imu_camera(sock_imu):
    start_timp = datetime.now()
    i=0
    while True:
        if (datetime.now() - start_timp).seconds <2:
            data_imu = sock_imu.recv(buf_size).decode("utf-8")	#vin sub forma de string
            if data_imu:
                vector_imu[i] = data_imu
                with open("distanta.txt", "r") as file:
                        continut = file.read()
                        if continut:
                            vector_camera[i] = float(continut)
                            print(f"{vector_imu[i]}->{vector_camera[i]}")
                            i+=1
        else:
            val_max= 0
            index=0
            for x in range(i):
                if int(vector_imu[x]) > int(val_max):
                    val_max=vector_imu[x]
                    index=x
            print(f"FFFFF {vector_imu[index]}->{vector_camera[index]}")
            i=0
            start_timp = datetime.now() 
            
            
        
             
        
	
def camera():
    #global data_camera
    continut_vechi = None
    while True:
            #with lock:
	    try:
                with open("distanta.txt", "r") as file:
                    continut = file.read().strip()
                    if continut != continut_vechi:
                        #vector_camera[index_c % buffer_size] = continut
                        continut_vechi = continut
                        #print(f"C{vector_camera[index_c % buffer_size]}")
                        timp = datetime.now().strftime("%H:%M:%S.%f")
                        #with lock:
                        #print(f"C{timp} - {continut}")
                        data_camera.append((timp, continut))
                        
	    except Exception as e:
                print("ex")
			
                        #index_c +=1
                        #print(f"C{vector_camera}")
                        #print(f"{vector_imu}->{vector_camera}")
                        #formatted_data = f"{identifier}{vector_camera}\n"
                        #sock_inel.send(formatted_data.encode('utf-8'))
	    time.sleep(0.05)
def corelare_imu_camera():
    #global data_imu, data_camera
    toleranta = 500
    while True:
        if data_imu and data_camera:
            print("alo")
            imu_data = data_imu.pop(0)
            camera_data =  data_camera.pop(0)
	    
            imu_timp, imu_val = imu_data
            camera_timp, camera_val = camera_data
	    
            imu_timp = datetime.strptime(imu_timp, "%H:%M:%S.%f")
            camera_timp = datetime.strptime(camera_timp, "%H:%M:%S.%f")
	    
            diferenta = abs((imu_timp - camera_timp).total_seconds() * 1000)
            print(f"{imu_timp} - cam {camera_timp}")
            print(diferenta)
            if diferenta<=toleranta:
                print(f"da {imu_val} {camera_val}")
            else:
                print("nu")
        #time.sleep(0.08)
	    
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
if sock1 is None or sock2 is None: #or sock3 is None:
    print("Failed to connect to ESP32 devices.")
    exit(1)


# Creează fire de execuție pentru fiecare ESP32
thread1 = threading.Thread(target=rx_and_echo, args=(sock1, 0))  # fluier
thread2 = threading.Thread(target=rx_and_echo, args=(sock2, 1))  # inel
thread3 = threading.Thread(target=input_and_send, args=(sock2,3))  # trimitere semnal pauza
#thread4 = threading.Thread(target=just_rx_and_echo, args=(sock3, ))  # vedem ce iese de la imu
thread5 = threading.Thread(target=imu_camera, args=(sock3, ))	#datele de la imu
#thread6 = threading.Thread(target=camera) 

thread1.start()
thread2.start()
thread3.start()
#thread4.start()
thread5.start()
#thread6.start()

# Așteaptă terminarea firelor
thread1.join()
thread2.join()
thread3.join()
#thread4.join()
thread5.join()
#thread6.join()

# Închide conexiunile
sock1.close()
sock2.close()
sock3.close()