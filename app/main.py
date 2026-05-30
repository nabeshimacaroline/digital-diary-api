from app import models
from fastapi import FastAPI
from app.database import engine
from app.routers import notes, events, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router)
app.include_router(notes.router)
app.include_router(events.router)

@app.get("/")
def root():
     return {"message": "Digital Diary API is alive!"}
