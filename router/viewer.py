from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

import pymongo
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


router = APIRouter(prefix="/viewer")


@router.get("/current")
def get_current(
    uid: Optional[str] = Query(None)
):
    col_current = db.current
    try:
        doc_current = (
            col_current.find({"uid": uid})
            .sort("time", pymongo.DESCENDING)
            .limit(1)
            .next()
        )
        doc_current = remove_objectId(doc_current)
        return doc_current
    except:
        return "no uid or no docs"


@router.get("/todo")
def get_todo(
    date: Optional[str] = Query(None, format="date"),
    uid: Optional[str] = Query(None)
):
    col_todo = db["todo"]
    if date is None:
        raise HTTPException(
            status_code=400, detail="Date query parameter is required")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    try:
        doc_todo = (
            col_todo.find({"uid": uid, "date": date})
            .sort("time", pymongo.DESCENDING)
            .limit(1)
            .next()
        )
        doc_todo = remove_objectId(doc_todo)
        return doc_todo
    except:
        return "no uid or no docs"
