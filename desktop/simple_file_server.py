import sys
import os
import asyncio
import argparse 
import base64

sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # add root of project to path

from __dependencies__.websockets import serve
from __dependencies__.quik_config import find_and_load

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
# html setup
# 
with open(info.path_to.face_html,'r') as f:
    html_file_content = f.read()
    html_file_content = html_file_content.replace("null/*UNQUE_ID_191093889137898240_address*/",f"'{config.desktop.ip_address}'")
    html_file_content = html_file_content.replace("null/*UNQUE_ID_19827378957898240_port*/",f"{config.desktop.web_socket_port}")
    html_file_content = html_file_content.encode('utf-8')
async def server_response(reader, writer): 
    writer.write("HTTP/1.1 200 OK\n".encode('utf-8'))
    writer.write("Content-Type: text/html; charset=utf-8\n".encode('utf-8'))
    writer.write(f"Content-Length: {len(html_file_content)}\n".encode('utf-8'))
    writer.write(html_file_content)
    await writer.drain()

async def main():
    print(f"open up http://{config.desktop.ip_address}:{config.desktop.file_server_port}")
    server1 = await asyncio.start_server(server_response, config.desktop.ip_address, config.desktop.file_server_port)
    await server1.serve_forever()

asyncio.run(main())