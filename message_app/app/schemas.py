# Pydanticのschema

from datetime import datetime
from pydantic import BaseModel, constr, field_validator

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# メッセージの基本的な構造を定義
class MessageBase(BaseModel):
    content: str

# メッセージ作成時の構造を定義。MessageBaseを継承しているためcontentを持つ。
class MessageCreate(MessageBase):
    # pydanticのconstrを使って、contentが空白でないことをチェックする
    # content: constr(min_length=1)

    # メッセージのフィールドごとにカスタムバリデーションを行う場合は、field_validatorデコレータを使う
    @field_validator('content')
    # Fieldごとのバリデーションだがclassmethodを使うのは、Pydanticの内部処理と一貫性のあるインターフェースを提供し、他のバリデーションと整合性を保つため
    @classmethod
    def check_content(cls, value):
        if len(value) < 1:
            raise ValueError('メッセージは1文字以上で送信してください')
        # strip():空白文字を削除するメソッド
        if value.strip() == "":
            raise ValueError('空白のメッセージは送信できません')
        return value

# DBから取得したメッセージを返す際の構造を定義。MessageBaseを継承しているためcontentを持つ。
class Message(MessageBase):
    id: int
    created_at: datetime

    # PydanticにSQLAlchemyのオブジェクトを返す際に必要な設定
    class Config:
        orm_mode = True

class MessageUpdate(MessageBase):
    pass