from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from firebase_admin import auth
import pymongo
from dependency import get_current_user
from db import db
from util import remove_objectId


class CurrentModel(BaseModel):
    current: Dict[str, Any]

class TodoItem(BaseModel):
    id: str
    type: str
    kind: str
    activity: Optional[Dict[str, Any]] = None
    addedTime: str
    plannedStartTime: Optional[str] = None
    actualStartTime: Optional[str] = None
    endTime: Optional[str] = None

class TodoData(BaseModel):
    date: str
    todos: List[TodoItem]


router = APIRouter(prefix="/controller")


@router.get("/")
def get_controller(user: auth.UserRecord = Depends(get_current_user)):
    col_current = db.current
    try:
        doc_current = (
            col_current.find({"uid": user.uid})
            .sort("time", pymongo.DESCENDING)
            .limit(1)
            .next()
        )
    except:
        doc_current = {
            "uid": user.uid,
            "time": datetime.now(),
            "current": {
                "display": "todo",
                "date": datetime.now(),
            },
        }
        col_current.insert_one(doc_current)
    doc_current = remove_objectId(doc_current)
    return doc_current

@router.post("/current")
def insert_current(
    data: CurrentModel, user: auth.UserRecord = Depends(get_current_user)
):
    col_current = db["current"]

    doc_current = {
        "uid": user.uid,
        "time": datetime.now(),
        "current": data.current,
    }

    result = col_current.insert_one(doc_current)

    if result.inserted_id:
        return {
            "status": "success",
            "message": "OK",
            "current": remove_objectId(doc_current),
        }
    else:
        return {"status": "failed", "message": "Insert failed"}

@router.get("/todo")
def get_todo(
    date: Optional[str] = Query(None, format="date"),
    user: auth.UserRecord = Depends(get_current_user)
):
    col_todo = db["todo"]
    if date is None:
        raise HTTPException(status_code=400, detail="Date query parameter is required")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    try:
        doc_todo = (
            col_todo.find({"uid": user.uid, "date": date})
            .sort("time", pymongo.DESCENDING)
            .limit(1)
            .next()
        )
    except:
        doc_todo = {
            "uid": user.uid,
            "time": datetime.now(),
            "date": date,
            "todos": [],
        }
        col_todo.insert_one(doc_todo)
    doc_todo = remove_objectId(doc_todo)
    return doc_todo

@router.post("/todo")
def insert_todo(
    data: TodoData, user: auth.UserRecord = Depends(get_current_user)
):
    col_todo = db.todo

    doc_todo = {
        "uid": user.uid,
        "time": datetime.now(),
        "date": data.date.split("T")[0],
        "todos": [todo.model_dump() for todo in data.todos],
    }

    result = col_todo.insert_one(doc_todo)

    if result.inserted_id:
        return {
            "status": "success",
            "message": "OK",
            "todos": remove_objectId(doc_todo),
        }
    else:
        return {"status": "failed", "message": "Insert failed"}