import random
import sys
import os
import asyncio
import argparse 
import base64
import ssl
import json
from time import sleep
from threading import Thread
from multiprocessing import Manager

sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # add root of project to path

from __dependencies__ import websockets
from __dependencies__.quik_config import find_and_load
from __dependencies__.blissful_basics import singleton, LazyDict, Warnings, print
from __dependencies__.websockets.sync.client import connect

# goals of this file:
    # receive data
    # talk to motors
    # talk to face

Warnings.disable()

info = find_and_load(
    "config.yaml",
    cd_to_filepath=True,
    fully_parse_args=True,
    defaults_for_local_data=[],
)
config = info.config

# 
# helpers
# 
manager = None # must be instantiated later
shared_data = None # must be instantiated later
def create_thread(function_being_wrapped):
    thread = Thread(target=function_being_wrapped)
    thread.start()
    return thread
ssl_context = ssl.SSLContext(cert_reqs=ssl.CERT_NONE)
# ssl_context.load_cert_chain(
#     info.absolute_path_to.file_server_public_key,
#     keyfile=info.absolute_path_to.file_server_private_key,
#     password=None,
# )

# 
# desktop thread
# 
Desktop = None
@singleton
class Desktop:
    url = f"wss://{config.desktop.ip_address}:{config.desktop.web_socket_port}/pi"
    websocket = None
    
    @staticmethod
    def query_faces():
        return shared_data["faces"]
    
    def listen_for_faces(*args):
        while 1:
            try:
                with connect(f"wss://{config.desktop.ip_address}:{config.desktop.web_socket_port}/pi", ssl_context=ssl_context) as websocket:
                    print("connected")
                    while 1:
                        print("waiting on /pi receive")
                        message = websocket.recv()
                        print("got some data")
                        try:
                            shared_data["faces"] = json.loads(message)
                        except Exception as error:
                            pass
            except Exception as error:
                print(f'''websocket connect error = {error}''')
                sleep(5)
    
    @staticmethod
    def tell_face(data):
        string = json.dumps(data)
        if not Desktop.websocket:
            with connect(Desktop.url, ssl_context=ssl_context) as websocket:
                Desktop.websocket = websocket
            
        websocket.send(string)


        
if __name__ == '__main__':
    manager = Manager()
    shared_data = manager.dict()
    # Desktop.tell_face(dict(showHappy=True))
    create_thread(Desktop.listen_for_faces)