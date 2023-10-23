from fastapi import  Request, HTTPException
from firebase_admin import auth
from db import db

def get_current_user(request: Request) -> auth.UserRecord:
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=403, detail="Token missing or malformed")
    
    token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        user = auth.get_user(decoded_token["uid"])
        col_user = db["user"]
        doc_user = col_user.find_one({"uid": user.uid})
        if not doc_user:
            doc_user = {
                "uid": user.uid,
                "email": user.email
            }
            col_user.insert_one(doc_user)
        return user
    except:
        raise HTTPException(status_code=403, detail="Invalid token or expired")

