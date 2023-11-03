import traceback
import asyncio
import queue
import time
import datetime

from db import db
from handler.viewer import current_handler

viewer_queue = queue.Queue()


async def async_current_handler(viewers, websocket, json_data):
    await current_handler(viewers, websocket, json_data)

async_handlers = {
    "current": async_current_handler,
}


def viewer_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            viewer_type, viewers, websocket, data_json = viewer_queue.get()
            check_message = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {data_json}"
            print(f"[WORKER]\t: {check_message}")

            if data_json["type"] != "init":
                col_log = db.Log
                col_log.insert_one(data_json)

            loop.run_until_complete(async_handlers[viewer_type](
                viewers, websocket, data_json))
            time.sleep(1)
        except:
            traceback.print_exc()
            continue
