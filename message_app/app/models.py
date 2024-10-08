# データベースモデル
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# SQLAlchemyのBaseクラスを取得する。これを使ってDBのテーブルとマッピングする
Base = declarative_base()

class Message(Base):
    # このクラスが紐づけられているテーブル名を指定
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
