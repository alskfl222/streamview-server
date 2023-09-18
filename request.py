import traceback
import queue
import time
import datetime

request_queue = queue.Queue()


def request_worker():
    while True:
        try:
            websocket, data = request_queue.get()
            if websocket is None:
                break
            response = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {data}"
            print(f"[WORKER]\t: {response}")
            time.sleep(3)
        except:
            traceback.print_exc()
            continue
