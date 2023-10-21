from fastapi import  Request, HTTPException
from firebase_admin import auth
from app import server

def get_current_user(request: Request) -> auth.UserRecord:
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=403, detail="Token missing or malformed")
    
    token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return auth.get_user(decoded_token["uid"])
    except:
        raise HTTPException(status_code=403, detail="Invalid token or expired")


def get_server():
    return server