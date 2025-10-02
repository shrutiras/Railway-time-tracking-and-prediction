from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
from models import Base, User
from auth import authenticate_user, get_password_hash, create_access_token, get_api_data

# Setup
load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "supersecret"))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Home redirect
@app.get("/", response_class=HTMLResponse)
def home():
    return RedirectResponse("/login")

# Login page
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

# Login POST
@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if user:
        request.session["user"] = user.username
        if user.role == "admin":
            return RedirectResponse("/admin/admin_dashboard", status_code=302)
        return RedirectResponse("/user/user_dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials", "user": None})

# Register page
@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "user": None})

# Register POST
@app.post("/register", response_class=HTMLResponse)
def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already registered", "user": None})
    hashed = get_password_hash(password)
    new_user = User(username=username, email=email, password=hashed, role="user")
    db.add(new_user)
    db.commit()
    return RedirectResponse("/login?msg=registered", status_code=302)

# User dashboard
@app.get("/user/user_dashboard", response_class=HTMLResponse)
def user_dashboard(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=302)
    user = db.query(User).filter(User.username == username).first()
    return templates.TemplateResponse("user/user_dashboard.html", {"request": request, "user": user})

# Admin dashboard (example)
@app.get("/admin/admin_dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=302)
    user = db.query(User).filter(User.username == username).first()
    if not user or user.role != "admin":
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("admin/admin_dashboard.html", {"request": request, "user": user})

# View trains page
@app.get("/user/view_trains", response_class=HTMLResponse, name="view_trains")

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
@app.get("/user/pnr_status", response_class=HTMLResponse, name="pnr_status")
def pnr_status_page(request: Request):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("user/pnr_status.html", {"request": request, "user": username})

# API to get train by number
@app.get("/trains/number/{train_number}")
def get_train_by_number(train_number: str):
    data = get_api_data()
    filtered = [t for t in data if t.get('train_number') == train_number]
    if not filtered:
        return JSONResponse(status_code=404, content={"error": "Train not found"})
    return filtered[0]

# API to get train by name
@app.get("/trains/name/{train_name}")
def get_train_by_name(train_name: str):
    data = get_api_data()
    filtered = [t for t in data if t.get('train_name', "").lower() == train_name.lower()]
    if not filtered:
        return JSONResponse(status_code=404, content={"error": "Train not found"})
    return filtered[0]
