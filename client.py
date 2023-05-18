import socket
import threading
from lightdjitellopy import Tello
import time
import json

TARGET_HOST = "localhost"
TARGET_PORT = 12345  

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind((TARGET_HOST, TARGET_PORT))

tello = Tello()

tello.connect()
#tello.takeoff()

globalDroneData : dict = {}

def ReceiveUDP():
    global globalDroneData
    while True:
        try:
            # Receive data from the server
            data, server_address = client_socket.recvfrom(1024)  
            code = json.loads(data.decode("utf-8"))

            #print("Data received:", code)
            
            globalDroneData = code


        except ConnectionRefusedError:
            print("Failed to connect to the server.")


udpThread = threading.Thread(target=ReceiveUDP)
udpThread.start()

class CachedInt:
    def __init__(self, value : int):
        self.value = value

    def Update(self, newValue) -> bool:
        """
            Updates the data with the latest intel. Return whether it has
            changed.
        """
        changed = newValue != self.value
        self.value = newValue

        return changed

    def __int__(self):
        return self.value

rightSignCode = CachedInt(0)
rightGestCode = CachedInt(0)
leftSignCode = CachedInt(0)
leftGestCode = CachedInt(0)
while True:
    cachedData = globalDroneData.copy()
    handCode = 0
    pointerPos = [0, 0]
    try:
        handCode = cachedData["hand_id"]
        pointerPos = cachedData["pointer"]
    except:
        print("Waiting for initial data...")
        time.sleep(0.1)
        continue
    
    try:
        if cachedData["num_hands"] == 2:
            leftChanged = rightSignCode.Update(cachedData["sign_id"])
            rightChanged = leftSignCode.Update(cachedData["sign_id"])

            if leftChanged and rightChanged:
                if int(rightSignCode) == 0 and int(leftSignCode) == 0:
                    tello.move_forward(30)

                if int(rightSignCode) == 2 and int(leftSignCode) == 2:
                    tello.flip_back()


        # Only respond to right hand for movement
        elif handCode == 1:
            if rightSignCode.Update(cachedData["sign_id"]):
                # Closed hands == forward
                # Removed due to conflict with pointer
                #if int(rightSignCode) == 1:
                #    tello.move_forward(30)

                #if int(rightSignCode) == 2:
                #    tello.send_rc_control(pointerPos[0], pointerPos[1], 30, 0)

                if int(rightSignCode) == 3:
                    tello.takeoff()
                    
            elif int(rightSignCode) == 2:
                rightGestCode.Update(cachedData["finger_gest_id"])
                if int(rightGestCode) == 1:
                    tello.rotate_clockwise(30);
                if int(rightGestCode) == 2:
                    tello.rotate_counter_clockwise(30);

        # Left hand for up, down, flip
        elif handCode == 0:
            if leftSignCode.Update(cachedData["sign_id"]):
                if int(leftSignCode) == 1:
                    tello.land()
    except:
        print("Weird random error occured, best not to think about it.")


    time.sleep(0.1)


# Close the socket
client_socket.close()


