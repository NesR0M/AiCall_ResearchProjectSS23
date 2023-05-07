import socket
import requests
import io
import base64
from PIL import Image, PngImagePlugin
from personal_key import PICTURE_HOST, PICTURE_PORT, STABLE_URL
from prompting import stableDifpayload

url = STABLE_URL

def send_image(client_socket, image_path):
    with open(image_path, 'rb') as file:
        image_data = file.read()
    image_size = len(image_data).to_bytes(4, byteorder='big')  # Convert image size to 4 bytes
    client_socket.sendall(image_size)  # Send the image size to the client
    client_socket.sendall(image_data)  # Send the image data to the client

def main():
    host = ''
    port = PICTURE_PORT
    image_path = 'output.png'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f'Server listening on {host}:{port}...')

    while True:
        client_socket, address = server_socket.accept()
        print(f'Connected to client: {address[0]}:{address[1]}')
        prompt = client_socket.recv(1024).decode()  # Receive the message from the client

        print(f'{url}/sdapi/v1/txt2img')
        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=stableDifpayload(prompt))
        #response = requests.post(url="http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload)
        r = response.json()
        print(r)
        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))
            image.save('output.png', pnginfo=pnginfo)
        
        send_image(client_socket, image_path)
        client_socket.close()
        print(f'{url}/sdapi/v1/txt2img')

if __name__ == '__main__':
    main()
