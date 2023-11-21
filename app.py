from typing import Any
import os
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import initialize_app, credentials
from dotenv import load_dotenv
from router import controller, viewer
from worker import viewer_worker, viewer_queue
from viewer.todo import todo_viewers
from handler.viewer import todo_viewer_init

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


@app.websocket("/todo/viewer/{todo_viewer_id}")
async def todo_viewer_endpoint(websocket: WebSocket, todo_viewer_id: str):
    await websocket.accept()
    todo_viewers[todo_viewer_id] = {"websocket": websocket}
    print(f"{todo_viewer_id} added to todo viewers")

    try:
        while True:
            data = await websocket.receive_json()
            await todo_viewer_init(websocket, data["uid"], data["date"])
    except WebSocketDisconnect:
        todo_viewers.pop(todo_viewer_id, None)
        print(f"{todo_viewer_id} removed from todo viewers")
    except:
        print("another error")
        print(todo_viewers)


origins = ["https://alskfl.info"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="http://localhost:.*|ws://localhost:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
