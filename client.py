import socket

TARGET_HOST = "localhost"
TARGET_PORT = 12345  

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind((TARGET_HOST, TARGET_PORT))

while True:
    try:
        # Receive data from the server
        data, server_address = client_socket.recvfrom(256)  

        print("Data received:", int.from_bytes(data, byteorder="big"))
    except ConnectionRefusedError:
        print("Failed to connect to the server.")

# Close the socket
client_socket.close()


