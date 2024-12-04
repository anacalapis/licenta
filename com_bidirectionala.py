import serial
from bluetooth import *

def input_and_send():
	print("\n Raspberry -> ESP32\n")
	while True:
		data = input()
		if len(data) == 0: break
		sock.send(data)
		sock.send("\n")
	
def rx_and_echo():
	#sock.send("\nESP -> Raspberry")
	while True:
		data = sock.recv(buf_size)
		if data:
			#print(data)
			data = data.decode("utf-8")
			print(data)
			ser.write(data.encode("utf-8"))
			#sock.send(data)
	
			
addr= "A0:A3:B3:97:55:46"
service_matches = find_service( address = addr )

buf_size = 1024;


if len(service_matches) == 0:
    print("couldn't find the SampleServer service =(")
    sys.exit(0)
    
#for s in range (len(service_matches)):
#	print("\nservice_matches[" + str(s) + "]:")
#	print(service_matches[s])
	
first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

#print("connecting to \"%s\" on %s" % (name, host))

# Create the client socket
sock=BluetoothSocket( RFCOMM )
sock.connect((host, port))

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

#input_and_send()
rx_and_echo()

sock.close()

