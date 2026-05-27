from fastapi import FastAPI
from pydantic import BaseModel
from app.services.agent import run_agent
from app.db.connection import query

app = FastAPI()

class Message(BaseModel):
    message: str

@app.post("/agent")
def agent_endpoint(payload: Message):
    print(f"Received message at /agent endpoint fastapi.main.py: {payload.message}")
    response = run_agent(payload.message)
    return {"response": response}

@app.get("/test-db")
def test_db():
    rows = query("SELECT * FROM customers LIMIT 5;")
    return {"rows": [dict(row._mapping) for row in rows]}
