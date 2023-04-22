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
with open(info.path_to.face_html,'rb') as f:
    html_file_content = f.read()
async def server_response(reader, writer): 
    writer.write("HTTP/1.1 200 OK\n".encode('utf-8'))
    writer.write("Content-Type: text/html; charset=utf-8\n".encode('utf-8'))
    writer.write(f"Content-Length: {len(html_file_content)}\n".encode('utf-8'))
    writer.write(html_file_content)
    await writer.drain()

async def main():
    print(f"open up http://localhost:{config.desktop.file_server_port}")
    server1 = await asyncio.start_server(server_response, "localhost", config.desktop.file_server_port)
    await server1.serve_forever()

asyncio.run(main())