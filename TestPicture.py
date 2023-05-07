import argparse
import requests
import io
import base64
from PIL import Image, PngImagePlugin
from personal_key import PICTURE_PORT, STABLE_URL
from prompting import stableDifpayload

url = STABLE_URL

def send_image(client_socket, image_path):
    with open(image_path, 'rb') as file:
        image_data = file.read()
    image_size = len(image_data).to_bytes(4, byteorder='big')  # Convert image size to 4 bytes
    client_socket.sendall(image_size)  # Send the image size to the client
    client_socket.sendall(image_data)  # Send the image data to the client

def main(prompt):
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=stableDifpayload(prompt))
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
        image.save('toDelete.png', pnginfo=pnginfo)

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-p', '--parameter', help='Parameter for main function', required=True)
    # args = parser.parse_args()
    main("ENTER A PROMPT TO TEST")