import socket
import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin

url = "http://127.0.0.1:7860"

def send_image(client_socket, image_path):
    with open(image_path, 'rb') as file:
        image_data = file.read()
    image_size = len(image_data).to_bytes(4, byteorder='big')  # Convert image size to 4 bytes
    client_socket.sendall(image_size)  # Send the image size to the client
    client_socket.sendall(image_data)  # Send the image data to the client

def main():
    host = ''
    port = 12345
    image_path = 'output.png'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f'Server listening on {host}:{port}...')

    while True:
        client_socket, address = server_socket.accept()
        print(f'Connected to client: {address[0]}:{address[1]}')
        prompt = client_socket.recv(1024).decode()  # Receive the message from the client

        payload = {
            "enable_hr": True,
            "denoising_strength": 0.52,
            "firstphase_width": 768,
            "firstphase_height": 512,
            "hr_scale": 2,
            "hr_upscaler": "Latent",
            "hr_second_pass_steps": 20,
            "prompt": prompt,
            "seed": -1,
            "sampler_name": "DPM++ 2M Karras",
            "steps": 25,
            "cfg_scale": 10,
            "width": 768,
            "height": 512,
            "negative_prompt": "EasyNegativeV2, badhandv4",
            "eta": 31337,
        }
        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        r = response.json()
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

if __name__ == '__main__':
    main()
