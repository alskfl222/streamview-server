import uuid
import datetime
from fastapi import WebSocket


async def current_handler(viewers, websocket: WebSocket, json_data):
    check_message = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {json_data}"
    print(f"[HANDLER]\t: {check_message}")
    if json_data['type'] == 'init':
        viewer_id = str(uuid.uuid4())
        viewers[viewer_id] = {'websocket': websocket, 'type': "current"}
        print(viewers)
        await websocket.send_json({"type": 'init', "viewer_id": viewer_id})
    if json_data['type'] == 'disconnect':
        viewers.pop(json_data['viewer_id'], None)
