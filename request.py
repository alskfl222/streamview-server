import os
import traceback
import asyncio
import queue
import time
import datetime

from handler.controller import controller_handler

request_queue = queue.Queue()

async def async_controller_handler(server, websocket, json_data):
    await controller_handler(server, websocket, json_data)

async_handlers = {
    "controller": async_controller_handler,
}

def request_worker():
    loop = asyncio.new_event_loop()  # 각 스레드에 대한 별도의 이벤트 루프 생성
    asyncio.set_event_loop(loop)
    
    while True:
        try:
            server, websocket, json_data = request_queue.get()
            if websocket is None:
                break
            check_message = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {json_data}"
            print(f"[WORKER]\t: {check_message}")

            sender = json_data["sender"]
            if sender['user'] == '':
                continue
            
            col_log = server.db.Log
            col_log.insert_one(json_data)

            sender_type = sender["type"]
            loop.run_until_complete(async_handlers[sender_type](server, websocket, json_data))
            time.sleep(1)
        except:
            traceback.print_exc()
            continue