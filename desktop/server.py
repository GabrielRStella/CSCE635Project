import sys
import os
import asyncio
import argparse 
import base64

sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # add root of project to path

import numpy                             # pip install numpy
import cv2                               # pip install opencv-python
from insightface.app import FaceAnalysis # pip install insightface onnxruntime
from __dependencies__ import json_fix
from __dependencies__.websockets import serve
from blissful_basics import singleton    # pip install blissful-basics
from quik_config import find_and_load    # pip install quik-config

# goals of this file:
    # provide index.html to phone
    # listen to phone input, send faces to pi
    # listen to pi input, send emotions to phone


# 
# args
# 
info = find_and_load(
    "config.yaml",
    cd_to_filepath=True,
    fully_parse_args=True,
    defaults_for_local_data=[],
)
config = info.config

# 
# face 
# 
print("\n\nthis is going to take like 15 seconds to load\n")
insightface_app = FaceAnalysis()
insightface_app.prepare(ctx_id=1, det_size=(config.image_width, config.image_height))
print("okay loaded")
class BoundingBox(list):
    """
    x_top_left, y_top_left, width, height format
    """
    
    @classmethod
    def from_points(cls, *points, top_left=None, bottom_right=None,):
        max_x = -float('Inf')
        max_y = -float('Inf')
        min_x = float('Inf')
        min_y = float('Inf')
        for each in [*points, top_left, bottom_right]:
            if type(each) != type(None):
                if max_x < each[0]:
                    max_x = each[0]
                if max_y < each[1]:
                    max_y = each[1]
                if min_x > each[0]:
                    min_x = each[0]
                if min_y > each[1]:
                    min_y = each[1]
        top_left = Position(min_x, min_y)
        bottom_right = Position(max_x, max_y)
        width  = abs(top_left.x - bottom_right.x)
        height = abs(top_left.y - bottom_right.y)
        return BoundingBox([ top_left.x, top_left.y, width, height ])
    
    @classmethod
    def from_array(cls, max_x, max_y, min_x, min_y):
        width  = abs(max_x - min_x)
        height = abs(max_y - min_y)
        return BoundingBox([ min_x, min_y, width, height ])
    
    @property
    def x_top_left(self): return self[0]
    
    @x_top_left.setter
    def x_top_left(self, value): self[0] = value
    
    @property
    def y_top_left(self): return self[1]
    
    @y_top_left.setter
    def y_top_left(self, value): self[1] = value
    
    @property
    def x_bottom_right(self): return self.x_top_left + self.width
    
    @property
    def y_bottom_right(self): return self.y_top_left + self.height
    
    @property
    def width(self): return self[2]
    
    @width.setter
    def width(self, value): self[2] = value
    
    @property
    def height(self): return self[3]
    
    @height.setter
    def height(self, value): self[3] = value
    
    @property
    def center(self):
        return [
            self.x_top_left + (self.width / 2),
            self.y_top_left + (self.height / 2),
        ]
    
    @property
    def area(self):
        return self.width * self.height
    
    def contains(self, point):
        x, y = point
        return (
            self.x_top_left     < x and
            self.x_bottom_right > x and
            self.y_top_left     < y and
            self.y_bottom_right > y
        )
        
    def __repr__(self):
        return f'[x_top_left={f"{self.x_top_left:.2f}".rjust(5)},y_top_left={f"{self.y_top_left:.2f}".rjust(5)},width={f"{self.width:.2f}".rjust(5)},height={f"{self.height:.2f}".rjust(5)}]'

class Face:
    def __init__(self, insight_face, image):
        self.image = image
        self.insight = insight_face
        image_height, image_width, *channels = self.image.shape
        # arrive in DEGREES
        pitch, yaw, roll = insight_face.pose
        self.nod    = pitch  # negative is down
        self.swivel = yaw    # left of the image is negative
        self.tilt   = roll   # if the person's face was a clock, then its negative when counter-clockwise
        self.width  = abs(self.insight.bbox[2] - self.insight.bbox[0])
        self.height = abs(self.insight.bbox[3] - self.insight.bbox[1])
        self.relative_width = self.width/image_width
        self.relative_height = self.height/image_height
    
    def __repr__(self):
        relative_x, relative_y = self.relative_position
        return f"Face(age={self.insight.age},nod={self.nod:.2f},swivel={self.swivel:.2f},tilt={self.tilt:.2f},height={self.height:.0f},width={self.width:.0f},relative_x={relative_x*100:.0f},relative_y={relative_y*100:.0f},)"
    
    @property
    def bounding_box(self):
        leftmost_x = self.insight.bbox[0]
        topmost_y = self.insight.bbox[1]
        return BoundingBox([ leftmost_x, topmost_y, self.width, self.height ])
    
    @property
    def relative_position(self):
        """
            Example:
                relative_x, relative_y = face.relative_position
                # the position is returned as a proportion, from -1 to 1
                # an x value of -1 means all the way to the right side of the picture
                # an y value of -1 means all the way to the top
        """
        face_x, face_y = self.bounding_box.center
        height, width, *channels = self.image.shape
        x_center = width/2
        y_center = height/2
        relative_x = (face_x - x_center)/x_center
        relative_y = (face_y - y_center)/y_center
        return relative_x, relative_y
    
    def __json__(self):
        relative_x, relative_y = self.relative_position
        return dict(
            nod=self.nod,
            swivel=self.swivel,
            tilt=self.tilt,
            relative_x=relative_x,
            relative_y=relative_y,
            relative_width=self.relative_width,
            relative_height=self.relative_height,
            age=self.insight.age,
        )

# 
# html setup
# 
with open(info.path_to.face_html,'rb') as f:
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
@singleton
class Pi:
    websocket = None

@singleton
class Phone:
    websocket = None

async def socket_response(websocket):
    if websocket.path == 'pi':
        Pi.websocket = websocket
        async for message in websocket: # message is a string sent from the webpage
            # forward emotion message to phone
            if Phone.websocket:
                Phone.websocket.send(message)
    elif websocket.path == "phone":
        Phone.websocket = websocket
        async for message in websocket: # message is a string sent from the webpage
            img = cv2.imdecode(numpy.frombuffer(base64.b64decode(message.encode('utf-8')), numpy.uint8), 1)
            height, width, *channels = img.shape
            faces = [ Face(each) for each in insightface_app.get(img) ]
            if Pi.websocket:
                Pi.send(json.dumps(faces))

# 
# start servers
# 
async def main():
    print(f"open up http://localhost:{config.desktop.server_port}")
    server1 = await asyncio.start_server(server_response, "localhost", config.desktop.server_port)
    server2 = await serve(socket_response, "localhost", config.desktop.socket_port)
    async with server1, server2:
        await asyncio.gather(server1.serve_forever(), server2.serve_forever())

asyncio.run(main())