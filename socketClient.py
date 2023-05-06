import socket
import os
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

def demo():
    # Set the source file path
    src_file = "images/example.png"

    # Set the destination file path
    dst_file = "images/copy_example.png"

    # Open the source PNG file for reading
    with open(src_file, 'rb') as fsrc:
        # Open the destination PNG file for writing
        with open(dst_file, 'wb') as fdst:
            # Copy the contents of the source file to the destination file
            fdst.write(fsrc.read())

    # Rename the new PNG file
    new_name = "images/output_0.png"
    if os.path.exists(new_name):
        os.remove(new_name)
    os.rename(dst_file, new_name)

def stablePicture(iteration, imagePrompt):
    host = PICTURE_HOST
    port = PICTURE_PORT
    image_path = f'images/output_{iteration}.png'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.connect((host, port))
        print(f'Connected to server: {host}:{port}')
        server_socket.sendall(imagePrompt.encode())  # Send the message to the server

        receive_image(server_socket, image_path)
        server_socket.close()
    except:
        # code to handle the exception
        demo()

    

