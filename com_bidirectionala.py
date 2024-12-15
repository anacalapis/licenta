from bluetooth import *
import serial
import threading

buf_size = 1024

# Adresele ESP32
addr_esp1 = "A0:A3:B3:97:55:46" #fluier
addr_esp2 = "A0:A3:B3:96:69:6A" #inel

data_sock0 = ""
data_sock1 = ""

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
        data = sock.recv(buf_size)
        if data:
            data = data.decode("utf-8")
            #print(f"{identifier}{data}")
            formatted_data = f"{identifier}{data}\n"
            ser.write(formatted_data.encode("utf-8"))
	    
def input_and_send(sock):
	while True:
		data = ser.readline().decode('utf-8').strip()
		#print(data)
		if data == "S" or data == "P":
		    print(data)
		    sock.send(data.encode('utf-8'))
		    sock.send("\n".encode('utf-8'))
		    ser.flush()  # Asigură-te că buffer-ul serial este golit


	
# Conectare la ESP32-urile
sock1 = connect_to_esp(addr_esp1) #fluier
sock2 = connect_to_esp(addr_esp2) #inel

# Asigură-te că ambele conexiuni sunt valide
if sock1 is None or sock2 is None:
    print("Failed to connect to one or both ESP32 devices.")
    exit(1)


# Creează fire de execuție pentru fiecare ESP32
thread1 = threading.Thread(target=rx_and_echo, args=(sock1, 0))  # fluier
thread2 = threading.Thread(target=rx_and_echo, args=(sock2, 1))  # inel
thread3 = threading.Thread(target=input_and_send, args=(sock2,))  # trimitere semnal pauza


thread1.start()
thread2.start()
thread3.start()

# Așteaptă terminarea firelor
thread1.join()
thread2.join()
thread3.join()

# Închide conexiunile
sock1.close()
sock2.close()
