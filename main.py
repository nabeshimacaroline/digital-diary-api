from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
     return {"mensagem": "API do Diário Digital está viva!"}