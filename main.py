from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os, requests

from database import SessionLocal, engine
from models import Base, User
from auth import authenticate_user, get_password_hash
from auth import get_api_data, create_access_token


# Setup
load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "supersecret"))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home():
    return RedirectResponse("/user/login")

# User Registration
@app.get("/user/register", response_class=HTMLResponse)
def user_register(request: Request):
    return templates.TemplateResponse("user/register.html", {"request": request})

@app.post("/user/register", response_class=HTMLResponse)
def user_register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("user/register.html", {"request": request, "error": "Email already exists"})
    hashed = get_password_hash(password)
    new_user = User(username=username, email=email, password=hashed, role="user")
    db.add(new_user)
    db.commit()
    return RedirectResponse("/user/login?msg=registered", status_code=302)

# User Login
# GET route: shows login page
@app.get("/user/login", response_class=HTMLResponse)
def login_page(request: Request, msg: str = None):
    return templates.TemplateResponse("user/login.html", {
        "request": request,
        "msg": msg
    })

# POST route: handles form submission
@app.post("/user/login", response_class=HTMLResponse)
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if user and user.role == "user":
        access_token = create_access_token(data={"sub": user.email})
        request.session["user"] = user.username
        request.session["token"] = access_token
        return RedirectResponse("/user/user_dashboard", status_code=302)
    return templates.TemplateResponse("user/login.html", {"request": request, "error": "Invalid credentials"})


# User Dashboard
@app.get("/user/user_dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/user/login", status_code=302)

    return templates.TemplateResponse("user/user_dashboard.html", {
        "request": request,
        "username": username
    })

# view trains
@app.get("/user/view_trains", response_class=HTMLResponse)
def user_view_trains(request: Request, fromStationCode: str = "", toStationCode: str = "", page: int = 1):
    page_size = 10
    all_trains = get_api_data(fromStationCode, toStationCode) 

    start = (page - 1) * page_size
    end = start + page_size
    trains = all_trains[start:end]

    return templates.TemplateResponse("user/view_trains.html", {
        "request": request,
        "trains": trains,
        "current_page": page,
        "total_pages": (len(all_trains) + page_size - 1) // page_size,
        "fromStationCode": fromStationCode,
        "toStationCode": toStationCode
    })


