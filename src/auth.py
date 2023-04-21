import secrets
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .database import Session, get_db
from .models import users as user_models
from .schemas.users import TokenData, User, UserCreate, UserInDB

SECRET_KEY = None
try:
    with open(".secret", "r") as file:
        SECRET_KEY = file.read()
except IOError:
    print("generating new key")
if not SECRET_KEY:
    # generate 32 hex digits using token hex
    SECRET_KEY = secrets.token_hex(32)
    with open(".secret", "w") as file:
        file.write(SECRET_KEY)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(
    db: Session,
    username: str,
):
    user = (
        db.query(user_models.User).filter(user_models.User.username == username).first()
    )
    if not user:
        return None
    return UserInDB(**user.__dict__.copy())


def authenticate_user(
    db: Session,
    username: str,
    password: str,
):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_user(
    db: Session,
    user: UserCreate,
):
    db_user = user_models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.cleartext_password),
        disabled=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def add_dummy_users_if_empty(db: Session = Depends(get_db)):
    if not db.query(user_models.User).first():
        create_user(
            db,
            UserCreate(
                username="foo", email="test@example.de", cleartext_password="bar"
            ),
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
