from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: str

    class Config:
        orm_mode = True


class User(BaseModel):
    username: str
    email: str
    full_name: str = ""
    disabled: bool = False

    class Config:
        orm_mode = True


class UserCreate(User):
    cleartext_password: str


class UserInDB(User):
    hashed_password: str
