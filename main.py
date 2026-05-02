from fastapi import FastAPI
import models
from database import engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
     return {"mensagem": "API do Diário Digital está viva!"}