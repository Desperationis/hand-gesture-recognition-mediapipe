import socket
import threading
from lightdjitellopy import TelloSwarm
import time

TARGET_HOST = "localhost"
TARGET_PORT = 12345  

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind((TARGET_HOST, TARGET_PORT))

swarm = TelloSwarm.fromIps([
    "192.168.5.198",
    ])

swarm.connect()
swarm.takeoff()

GLOBAL_CODE = 0

def ReceiveUDP():
    global GLOBAL_CODE
    while True:
        try:
            # Receive data from the server
            data, server_address = client_socket.recvfrom(256)  
            code = int.from_bytes(data, byteorder="big")
            print("Data received:", code)
            
            GLOBAL_CODE = code


        except ConnectionRefusedError:
            print("Failed to connect to the server.")


udpThread = threading.Thread(target=ReceiveUDP)
udpThread.start()

previousCode = 0
while True:
    cachedCode = GLOBAL_CODE
    if cachedCode != previousCode:
        if cachedCode == 1:
            swarm.flip_left()

        if cachedCode == 2:
            swarm.flip_right()

        if cachedCode == 3:
            swarm.land()

    previousCode = cachedCode

    time.sleep(0.1)


# Close the socket
client_socket.close()


