from typing import Dict, Any
import datetime
import pymongo
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from firebase_admin import auth
from dependency import get_current_user
from db import db
from util import remove_objectId


class CurrentInsert(BaseModel):
    current: Dict[str, Any]


router = APIRouter(prefix="/controller")


@router.get("/")
def get_controller(user: auth.UserRecord = Depends(get_current_user)):
    col_current = db["current"]
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
            "time": datetime.datetime.utcnow(),
            "current": {
                "display": "todo",
                "date": datetime.datetime.utcnow(),
            },
        }
        col_current.insert_one(doc_current)
    doc_current = remove_objectId(doc_current)
    return doc_current

@router.post("/current")
def insert_current(
    data: CurrentInsert, user: auth.UserRecord = Depends(get_current_user)
):
    col_current = db["current"]

    doc_current = {
        "uid": user.uid,
        "time": datetime.datetime.utcnow(),
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
