from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.data import sessions_db
from app.schemas import SessionCreate, SessionOut

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/sessions", response_model=list[SessionOut])
def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: str | None = None,
):
    items = sessions_db
    if search:
        term = search.lower()
        items = [
            s for s in items if term in s["route"].lower() or term in s["driver"].lower()
        ]
    return items[skip : skip + limit]


@app.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: int):
    for session in sessions_db:
        if session["id"] == session_id:
            return session
    raise HTTPException(status_code=404, detail="Session not found")


@app.post("/sessions", response_model=SessionOut, status_code=201)
def create_session(payload: SessionCreate):
    new_id = max((s["id"] for s in sessions_db), default=0) + 1
    session = {"id": new_id, **payload.model_dump()}
    sessions_db.append(session)
    return session


@app.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int):
    for index, session in enumerate(sessions_db):
        if session["id"] == session_id:
            sessions_db.pop(index)
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail="Session not found")
