from fastapi import FastAPI
from dbservice import *
from pydanticmodel import *
from fastapi.middleware.cors import CORSMiddleware
from security import *



app = FastAPI()
db = SessionLocal()

origins = [
    "http://localhost",
    "http://localhost:5173"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.post("/register")
def addUser(user : UserCreate):
    password = pwd_context.hash(user.password)
    existinguser = db.query(User).filter(User.username == user.username).first()
    if not existinguser:
       new_user = User(username=user.username , email=user.email , contact=user.contact , password = password)
       db.add(new_user)
       db.commit()
       db.refresh(new_user)
       db.close()
    else:
         db.rollback()
         raise HTTPException(
            status_code=400, detail="Username already registered")
        
    
         


       
       
    


