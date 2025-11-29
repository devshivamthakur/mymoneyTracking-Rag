
from app.DB.FireBaseInit import firebase_db
from fastapi import HTTPException
from app.auth import create_access_token, create_refresh_token

def validate_user(userId: str) -> dict:
    # Check if user exists in Firestore
    user_ref = firebase_db.collection('users').document(userId)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found.")
    # If user exists, return some user data or tokens as needed
    print("User validated:", userId, user_doc.to_dict())
    accessToken = create_access_token(userId)
    refreshToken = create_refresh_token(userId)
    return {"access_token": accessToken, "refresh_token": refreshToken}

def get_user_info(userId: str):
    user_ref = firebase_db.collection('users').document(userId)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found.")
    if not user_doc.to_dict():
        raise HTTPException(status_code=404, detail="User data is empty.")
    return {k: v for k, v in user_doc.to_dict().items() if k != 'google_id'}
    