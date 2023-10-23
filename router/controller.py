import datetime
import pymongo
from fastapi import APIRouter, Depends
from firebase_admin import auth
from dependency import get_current_user
from db import db
from util import remove_objectId

router = APIRouter(prefix="/controller")


@router.get("/")
def get_controller(user: auth.UserRecord = Depends(get_current_user)):
    col_current = db["current"]
    try:
        doc_current = col_current.find({"uid": user.uid}).sort(
            "time", pymongo.DESCENDING).limit(1).next()
    except:
        doc_current = {
            "uid": user.uid,
            "time": datetime.datetime.utcnow(),
            "current": {
                "display": "todo",
                "date": datetime.datetime.utcnow(),
            }
        }
        col_current.insert_one(doc_current)
    doc_current = remove_objectId(doc_current)
    return doc_current
