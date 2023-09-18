import threading
import datetime
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from request import request_worker, request_queue

app = FastAPI()

controller_client = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            print(f"[APP]\t\t: {datetime.datetime.now():%Y-%m-%d %H:%M:%S} : {data}")
            request_queue.put((websocket, data))  # 웹소켓 및 데이터를 큐에 넣습니다.
        except WebSocketDisconnect:
            break

if __name__ == "__main__":
    threading.Thread(target=request_worker, daemon=True).start()  # 워커 스레드를 시작합니다.

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
