import traceback
import queue
import time
import datetime
import asyncio
import os
import pymongo
import certifi
from dotenv import load_dotenv
from handler.controller import controller_handler

load_dotenv()
ENV = os.getenv("ENV")
DBID = os.getenv("MONGODB_ID")
DBPW = os.getenv("MONGODB_PW")
atlas_link = f"mongodb+srv://{DBID}:{DBPW}@info.syvdo.mongodb.net/info?retryWrites=true&w=majority"

dbclient = pymongo.MongoClient(atlas_link, tlsCAFile=certifi.where())
db = dbclient["StreamView"]
col_log = db.Log

request_queue = queue.Queue()

async def async_controller_handler(server, websocket, json_data):
    await controller_handler(server, websocket, json_data)

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
            
            if "sender" not in json_data.keys():
                print("invalid message")
                response = {
                    "status": "error",
                    "message": "Invalid message format. 'sender' key missing."
                }
                loop.run_until_complete(websocket.send_json(response))
            else:
                sender = json_data["sender"]
                if not sender['type']['user']:
                    continue
                col_log.insert_one(json_data)
                if sender['type'] == 'controller':
                    loop.run_until_complete(async_controller_handler(server, websocket, json_data))
                time.sleep(1)
        except:
            traceback.print_exc()
            continue