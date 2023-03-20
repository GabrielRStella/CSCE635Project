import asyncio
import websockets
import random
import json

from quik_config import find_and_load            # pip install quik-config
from blissful_basics import singleton, LazyDict  # pip install blissful-basics

from async_tools import asyncify, main
# goals of this file:
    # receive data
    # talk to motors
    # talk to face


info = find_and_load(
    "config.yaml",
    cd_to_filepath=True,
    fully_parse_args=True,
    defaults_for_local_data=[],
)
config = info.config

@singleton
class Brain:
    most_recent_faces = []


@singleton
class Desktop:
    url = f"ws://{config.desktop.ip_address}:{config.desktop.socket_port}/pi"
    websocket = None
    timeout_seconds = 0.5
    
    @asyncify()
    async def try_to_connect(self):
        while True:
            try:
                async with connect(self.url) as websocket:
                    self.websocket = websocket
            except Exception as error:
                print(f'''websocket connect error = {error}''')
                await asyncio.sleep(self.timeout_seconds)

    # When getting data from desktop
    @asyncify()
    async def handle_incoming_messages(self):
        while True:
            # wait until connect/reconnect
            if not self.websocket:
                await asyncio.sleep(1)
            # then await messages
            message = await self.websocket.recv()
            
            # TODO: maybe message.result()
            faces = json.parse(message)
            Brain.most_recent_faces = [ LazyDict(each) for each in faces ]
    
    @asyncify()
    async def tell_face(self, data):
        string = json.dumps(data)
        if self.websocket:
            await self.websocket.send(string)
            
@main
async def _():
    # start trying to connect
    Desktop.try_to_connect()
    Desktop.handle_incoming_messages()
    
    while True:
        if len(Brain.most_recent_faces) > 0:
            Desktop.tell_face(dict(is_happy=True))
        
        