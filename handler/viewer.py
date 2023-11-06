import traceback
import pymongo
from fastapi import WebSocket
from db import db
from util import remove_objectId

async def todo_handler(websocket: WebSocket, uid: str, date: str):
    col_todo = db.todo
    try:
        doc_todo = (
            col_todo.find({"uid": uid, "date": date})
            .sort("time", pymongo.DESCENDING)
            .limit(1)
            .next()
        )
        print(type(doc_todo))
        print(doc_todo)
        doc_todo = remove_objectId(doc_todo)
        doc_todo = {
            **doc_todo,
            'time': doc_todo['time'].isoformat(),
        }
        await websocket.send_json(doc_todo)
    except:
        traceback.print_exc()
        return "no uid or no docs"

