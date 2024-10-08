# FastAPIのエントリーポイント（APIのルート）
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from message_app.app import crud, models, schemas, auth
from message_app.app.database import get_db, engine

description = """
# API Documentation

## `POST /users/`
### Description:
Create a new user in the system.

- **Request Body**: 
  - `schemas.UserCreate`: User information, including email, password.
  
- **Response**: 
  - Returns the created user object.

- **Error Responses**: 
  - `400`: If the email is already registered.

---

## `POST /token`
### Description:
Authenticate a user and issue an access token.

- **Request Body**: 
  - `OAuth2PasswordRequestForm`: Contains username (email) and password.

- **Response**: 
  - Returns an access token for the user and its type.

- **Error Responses**: 
  - `401`: If the credentials are invalid.

---

## `GET /messages/`
### Description:
Retrieve a list of messages with pagination.

- **Query Parameters**: 
  - `skip`: Number of messages to skip (default: 0).
  - `limit`: Maximum number of messages to return (default: 10).

- **Response**: 
  - Returns a list of messages as defined by `schemas.Message`.

- **Error Responses**: 
  - `404`: If no messages are found.

---

## `POST /messages/`
### Description:
Create a new message.

- **Request Body**: 
  - `schemas.MessageCreate`: Message content.

- **Response**: 
  - Returns the created message object.

- **Error Responses**: 
  - `401`: If the user is not authenticated.

---

## `PUT /messages/{message_id}`
### Description:
Update an existing message.

- **Path Parameters**: 
  - `message_id`: ID of the message to update.

- **Request Body**: 
  - `schemas.MessageUpdate`: New content for the message.

- **Response**: 
  - Returns the updated message object.

- **Error Responses**: 
  - `404`: If the message with the specified ID is not found.

---

## `DELETE /messages/{message_id}`
### Description:
Delete a message.

- **Path Parameters**: 
  - `message_id`: ID of the message to delete.

- **Response**: 
  - Confirms that the message was deleted.

- **Error Responses**: 
  - `404`: If the message with the specified ID is not found.
  - `401`: If the user is not authenticated.

"""

# DBのマイグレーションと同じことをしている。
models.Base.metadata.create_all(bind=engine)

# FastAPIのインスタンスを生成
app = FastAPI(description=description)

# OAuth2のBearer Tokenを使って認証するためのスキームを定義
outh2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ユーザーを作成するエンドポイント
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="このメールアドレスはすでに登録されています")
    return crud.create_user(db=db, user=user)


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="無効な認証情報")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(db: Session = Depends(get_db), token: str = Depends(outh2_scheme)):
    payload = auth.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="無効なトークン")
    user = crud.get_user_by_email(db, email=payload.get("sub"))
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return user

# メッセージを取得するエンドポイント
# response_modelはレスポンスの構造を指定する
@app.get("/messages/", response_model=list[schemas.Message])
# DpendesはFastAPIの依存性注入機能を使ってDBセッションを取得する
def read_messages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    messages = crud.get_messages(db, skip=skip, limit=limit)
    if messages is None:
        raise HTTPException(status_code=404, detail="Messages not found")
    return messages

# メッセージを作成するエンドポイント
@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_message(db=db, message=message)

@app.put("/messages/{message_id}", response_model=schemas.Message)
def update_message(id: int, message: schemas.MessageUpdate, db: Session = Depends(get_db)):
    old_message = crud.get_message_by_id(db=db, id=id)
    if old_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return crud.update_message(db=db, new_message=message, id=id)

@app.delete("/messages/{message_id}")
def delete_message(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    old_message = crud.get_message_by_id(db=db, id=id)
    if old_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return crud.delete_message(db=db, id=id)
