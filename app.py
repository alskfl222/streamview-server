from typing import Any
import asyncio
import os
import threading
import datetime
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import initialize_app, credentials
from dotenv import load_dotenv
from router import controller, viewer
from worker import viewer_worker, viewer_queue

load_dotenv()

app = FastAPI()
current_viewers: dict[str, WebSocket] = {}


threading.Thread(target=viewer_worker, daemon=True).start()

CREDENTIAL_PATH = os.getenv("CREDENTIAL_PATH")
firebase_credentials = credentials.Certificate(CREDENTIAL_PATH)
initialize_app(firebase_credentials)


@app.get("/health")
def health_check():
    return "api ok"


app.include_router(controller.router)
app.include_router(viewer.router)


@app.websocket("/current/{current_viewer_id}")
async def current_websocket_endpoint(websocket: WebSocket, current_viewer_id: str):
    await websocket.accept()
    current_viewers[current_viewer_id] = websocket
    print(f"{current_viewer_id} added to current viewers")
    
    # async def ping_client():
    #     while True:
    #         try:
    #             await websocket.send_text("ping")
    #             await asyncio.sleep(5) # 5초
    #         except asyncio.CancelledError:
    #             break

    # ping_task = asyncio.create_task(ping_client())
    
    try:
        while True:
            data = await websocket.receive_text()
            # if data == "pong":
            #     print(f"Pong received from {current_viewer_id}")
            #     continue
    except WebSocketDisconnect:
        # ping_task.cancel()  # Cancel the ping task on disconnect
        current_viewers.pop(current_viewer_id, None)
        print(f"{current_viewer_id} removed from current viewers")


origins = [
    "https://alskfl.info"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="http://localhost:.*|ws://localhost:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
