# auth.py

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User
from database import SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
load_dotenv()

# Load the secret key from .env or define it directly
SECRET_KEY = os.getenv("JWT_Secret_Key", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
import requests


def get_api_data(from_station: str, to_station: str):
    # Example code for calling your API
    import os
    import requests

    base_url = os.getenv("API_BASE_URL")  # Make sure it's in .env
    api_key = os.getenv("API_KEY")        # API key from .env

    if not base_url or not api_key:
        print("API configuration missing.")
        return []

    try:
        url = f"{base_url}?fromStationCode={from_station}&toStationCode={to_station}"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])  # Return list of trains or empty list
    except Exception as e:
        print(f"API error: {e}")
        return []


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Password utils
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Authenticate user
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.password):
        return user
    return None

# ✅ ADD THIS FUNCTION TO FIX THE ERROR
def get_current_user(request):
    username = request.session.get("user") or request.session.get("admin")
    if not username:
        return None
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    return user
