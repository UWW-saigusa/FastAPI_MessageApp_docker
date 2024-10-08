# データベース接続設定

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLiteによって作成されるファイル形式のDB（test.db）へのパスを指定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# SQLAlchemyにDBへの接続を指示。さらに複数のスレッドでの接続を許可。
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# DBセッションを管理するためのセッションファクトリを作成
# autocommit=False, autoflush=False は、セッションが自動的にコミットされないようにするための設定
# bind=engineは、どのDBにをセッションに紐づけるかを指定
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 呼び出し元にセッションを渡すジェネレータ関数
def get_db():
    # DBセッションのインスタンスを生成
    db = SessionLocal()
    try:
        # リクエストが完了するまでセッションを維持
        yield db
    finally:
        # リクエストが完了するとセッションを自動的に閉じる
        db.close()