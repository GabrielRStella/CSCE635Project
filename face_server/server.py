import asyncio
import argparse 
import base64

import numpy                             # pip install numpy
import cv2                               # pip install opencv-python
from websockets import serve             # pip install websockets 
from insightface.app import FaceAnalysis # pip install insightface onnxruntime

# 
# args
# 
parser = argparse.ArgumentParser(description="aiohttp server") 
parser.add_argument('--server-port', default=8080)
parser.add_argument('--socket-port', default=9093)
parser.add_argument('--image-height', default=680)
parser.add_argument('--image-width', default=680)
args = parser.parse_args()


# 
# face 
# 
print("\n\nthis is going to take like 15 seconds to load\n")
insightface_app = FaceAnalysis()
insightface_app.prepare(ctx_id=1, det_size=(args.image_width, args.image_height))
print("okay loaded")

# 
# html setup
# 
with open('index.html','rb') as f:
    html_file_content = f.read()
async def server_response(reader, writer): 
    writer.write("HTTP/1.1 200 OK\n".encode('utf-8'))
    writer.write("Content-Type: text/html; charset=utf-8\n".encode('utf-8'))
    writer.write(f"Content-Length: {len(html_file_content)}\n".encode('utf-8'))
    writer.write(html_file_content)
    await writer.drain()


# 
# socket setup
# 
async def socket_response(websocket):
    async for message in websocket: # message is a string sent from the webpage
        img = cv2.imdecode(numpy.frombuffer(base64.b64decode(message.encode('utf-8')), numpy.uint8), 1)
        faces = insightface_app.get(img)
        print(f'''len(faces) = {len(faces)}''')

# 
# start servers
# 
async def main():
    print(f"open up http://localhost:{args.server_port}")
    server1 = await asyncio.start_server(server_response, "localhost", args.server_port)
    server2 = await serve(socket_response, "localhost", args.socket_port)
    async with server1, server2:
        await asyncio.gather(server1.serve_forever(), server2.serve_forever())

asyncio.run(main())