import datetime


async def controller_handler(server, websocket, json_data):
    check_message = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {json_data}"
    print(f"[HANDLER]\t: {check_message}")
    if json_data['type'] == 'current':
        message = {**json_data, "sender": "server"}
        await websocket.send_json(message)
