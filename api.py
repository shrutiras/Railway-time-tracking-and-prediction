# api.py
from fastapi import APIRouter, Depends, HTTPException
from models import User, Train
from database import SessionLocal
from sqlalchemy.orm import Session
from auth import create_access_token, verify_password, get_current_user
from pydantic import BaseModel

router = APIRouter()

class LoginForm(BaseModel):
    email: str
    password: str

class RegisterForm(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"

class TrainForm(BaseModel):
    name: str
    route: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("user/register")
def register(user: RegisterForm, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/user/login?msg=registered", status_code=302)

    return {"detail": "User registered"}

@router.post("/login")
def login(form: LoginForm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.email).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email, "role": user.role})
    return {"token": token, "role": user.role}

@router.get("/trains")
def get_trains(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Train).all()

@router.post("/add_train")
def add_train(train: TrainForm, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    new_train = Train(**train.dict())
    db.add(new_train)
    db.commit()
    return {"detail": "Train added"}

@router.get("/users")
def get_users(user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    return db.query(User).all()
