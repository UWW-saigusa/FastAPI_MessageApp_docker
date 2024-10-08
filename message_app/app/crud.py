# CRUD操作を定義

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from . import models, schemas, auth

# ユーザーを取得
def get_user_by_email(db: Session, email: str):
    try:
        return db.query(models.User).filter(models.User.email == email).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ユーザーを作成
def create_user(db: Session, user: schemas.UserCreate):
    try:
        db_user = models.User(email=user.email, hashed_password=auth.get_password_hash(user.password))
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# メッセージを取得
# skip: 何件目から取得するか
# limit: 何件取得するか
# db: Session のコロン以降は型ヒント（アノテーション）
def get_messages(db: Session, skip: int = 0, limit: int = 10):
    try:
        return db.query(models.Message).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# メッセージをIDで取得
def get_message_by_id(db: Session, id: int):
    try:
        return db.query(models.Message).filter(models.Message.id == id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# メッセージを作成
def create_message(db: Session, message: schemas.MessageCreate):
    try:
        db_message = models.Message(content=message.content)
        db.add(db_message)
        db.commit()
        # 自動生成される値（ID、created_at）を取得するためにリフレッシュ
        db.refresh(db_message)
        return db_message
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_message(db: Session, new_message: schemas.MessageUpdate, id: int):
    try:
        db_message = db.query(models.Message).filter(models.Message.id == id).first()
        db_message.content = new_message.content
        db.commit()
        db.refresh(db_message)
        return db_message
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def delete_message(db: Session, id: int):
    try:
        db_message = db.query(models.Message).filter(models.Message.id == id).first()
        db.delete(db_message)
        db.commit()
        return "delete complete"
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
   