from typing import Any
import os
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import initialize_app, credentials
from dotenv import load_dotenv
from router import controller, viewer
from worker import viewer_worker, viewer_queue
from viewer.todo import todo_viewers, todo_currents
from handler.viewer import todo_init

load_dotenv()

app = FastAPI()


threading.Thread(target=viewer_worker, daemon=True).start()

CREDENTIAL_PATH = os.getenv("CREDENTIAL_PATH")
firebase_credentials = credentials.Certificate(CREDENTIAL_PATH)
initialize_app(firebase_credentials)


@app.get("/health")
def health_check():
    return "api ok"


app.include_router(controller.router)
app.include_router(viewer.router)


@app.websocket("/viewer/todo/{todo_viewer_id}")
async def todo_viewer_endpoint(websocket: WebSocket, todo_viewer_id: str):
    await websocket.accept()
    todo_viewers[todo_viewer_id] = {"websocket": websocket}
    print(f"{todo_viewer_id} added to todo viewers")

    try:
        while True:
            data = await websocket.receive_json()
            await todo_init(websocket, data["uid"], data["date"])
    except WebSocketDisconnect:
        todo_viewers.pop(todo_viewer_id, None)
        print(f"{todo_viewer_id} removed from todo viewers")
    except:
        print("another error")
        print(todo_viewers)

@app.websocket("/viewer/current/{todo_current_id}")
async def todo_current_endpoint(websocket: WebSocket, todo_current_id: str):
    await websocket.accept()
    todo_currents[todo_current_id] = {"websocket": websocket}
    print(f"{todo_current_id} added to todo currents")

    try:
        while True:
            data = await websocket.receive_json()
            await todo_init(websocket, data["uid"], data["date"])
    except WebSocketDisconnect:
        todo_currents.pop(todo_current_id, None)
        print(f"{todo_current_id} removed from todo currents")
    except:
        print("another error")
        print(todo_currents)

origins = ["https://alskfl.info"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="http://localhost:.*|ws://localhost:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
