import os
import threading
import datetime
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import initialize_app, credentials
from dotenv import load_dotenv
from router import controller
from request import request_worker, request_queue

load_dotenv()

app = FastAPI()
viewers: dict[str, WebSocket] = {}


threading.Thread(target=request_worker, daemon=True).start()

CREDENTIAL_PATH = os.getenv("CREDENTIAL_PATH")
firebase_credentials = credentials.Certificate(CREDENTIAL_PATH)
initialize_app(firebase_credentials)


@app.get("/health")
def health_check():
    return "api ok"


app.include_router(controller.router)


@app.websocket("ws")
async def websocket_endpoint(self, websocket: WebSocket):
    await websocket.accept()
    viewer_id = uuid.uuid4()
    viewers[viewer_id] = websocket
    while True:
        try:
            json_data = await websocket.receive_json()
            print(
                f"[APP]\t\t: {datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {json_data}")
            request_queue.put((self, websocket, json_data))
        except WebSocketDisconnect:
            viewers.pop(viewer_id)

origins = [
    "https://alskfl.info"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="http://localhost:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
