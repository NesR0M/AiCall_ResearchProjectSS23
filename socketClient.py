import socket
from personal_key import PICTURE_HOST, PICTURE_PORT 

def receive_image(server_socket, image_path):
    image_size = int.from_bytes(server_socket.recv(4), byteorder='big')
    image_data = b''

    while len(image_data) < image_size:
        data = server_socket.recv(1024)
        if not data:
            break
        image_data += data

    with open(image_path, 'wb') as file:
        file.write(image_data)
        
    print(f'Image received and saved as {image_path}')

def stablePicture(iteration, imagePrompt):
    host = PICTURE_HOST
    port = PICTURE_PORT
    image_path = f'images/output_{iteration}.png'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((host, port))
    print(f'Connected to server: {host}:{port}')

    server_socket.sendall(imagePrompt.encode())  # Send the message to the server

    receive_image(server_socket, image_path)
    server_socket.close()

