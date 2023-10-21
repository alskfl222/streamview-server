import os
import threading
import datetime
import uuid
import pymongo
import certifi
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import initialize_app, credentials
from dotenv import load_dotenv
from router import controller
from request import request_worker, request_queue


class StreamViewServer:
    def __init__(self):
        self.app = FastAPI()
        self.viewers: dict[str, WebSocket] = {}
        load_dotenv()
        # ENV = os.getenv("ENV")
        DBID = os.getenv("MONGODB_ID")
        DBPW = os.getenv("MONGODB_PW")
        atlas_link = f"mongodb+srv://{DBID}:{DBPW}@info.syvdo.mongodb.net/info?retryWrites=true&w=majority"
        dbclient = pymongo.MongoClient(atlas_link, tlsCAFile=certifi.where())
        db = dbclient["StreamView"]
        self.db = db

        self.status = {
            "current": {
                "display": "할일",
                "date": datetime.datetime.now().isoformat(),
            },
        }

    def run(self):
        threading.Thread(target=request_worker, daemon=True).start()

        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=5005)

server = StreamViewServer()

firebase_credentials = credentials.Certificate("server_credentials.json")
initialize_app(firebase_credentials)

@server.app.get("/health")
def health_check():
    return "api ok"

server.app.include_router(controller.router)

@server.app.websocket("ws")
async def websocket_endpoint(self, websocket: WebSocket):
    await websocket.accept()
    viewer_id = uuid.uuid4()
    server.viewers[viewer_id] = websocket
    while True:
        try:
            json_data = await websocket.receive_json()
            print(
                f"[APP]\t\t: {datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {json_data}")
            request_queue.put((self, websocket, json_data))
        except WebSocketDisconnect:
            server.viewers.pop(viewer_id)

origins = [
    "https://alskfl.info"
]


server.app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="http://localhost:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    server.run()
