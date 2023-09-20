import threading
import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from request import request_worker, request_queue


class StreamViewServer:
    def __init__(self):
        self.app = FastAPI()
        self.controller_client = {}
        self.app.websocket("/ws")(self.websocket_endpoint)
        self.status = {
            "category": {
                "main": "charactor",
                "sub": "current",
            },
            "data": {
                "name": "1111"
            }
        }

    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()
        while True:
            try:
                json_data = await websocket.receive_json()
                print(
                    f"[APP]\t\t: {datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {json_data}")
                request_queue.put((self, websocket, json_data))
            except WebSocketDisconnect:
                break

    def run(self):
        threading.Thread(target=request_worker, daemon=True).start()

        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    server = StreamViewServer()
    server.run()
