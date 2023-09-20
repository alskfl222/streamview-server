import traceback
import queue
import time
import datetime
from handler.controller import controller_handler

request_queue = queue.Queue()


def request_worker():
    while True:
        try:
            server, websocket, json_data = request_queue.get()
            if websocket is None:
                break
            check_message = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {json_data}"
            print(f"[WORKER]\t: {check_message}")
            if "sender" in json_data.keys():
                print("invalid message")
            else:
                sender = json_data["sender"]
                if sender == "controller":
                    controller_handler(server, websocket, json_data)
                time.sleep(1)
        except:
            traceback.print_exc()
            continue
