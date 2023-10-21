from fastapi import APIRouter, Depends
from firebase_admin import auth
from dependency import get_current_user, get_server

router = APIRouter()

@router.get("/controller")
def get_controller(
    current_user: auth.UserRecord = Depends(get_current_user),
    server = Depends(get_server)):
    print(current_user.uid)
    return {"status": "Controller active", "data": server.status}