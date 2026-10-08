from fastapi import FastAPI, HTTPException, Depends
from app.core.database import SessionLocal, init_db
from app.models.lap_summary import LapSummary
from sqlalchemy.orm import Session
from app.models.pydantic_models import SessionRequest
from app.pipeline.ingestion import save_session_summary_to_db

init_db()

app = FastAPI(title="F1 Insights & Strategy Engine")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/lap-summaries")
def get_lap_summaries(driver: str | None = None, grand_prix: str | None = None, db: Session = Depends(get_db)):
    query = db.query(LapSummary)

    if driver:
        query = query.filter(LapSummary.driver == driver)
    if grand_prix:
        query = query.filter(LapSummary.grand_prix == grand_prix)

    results = query.all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found!")
    
    return {"summaries": results}

@app.post("/fetch-session")
def fetch_session(session_request: SessionRequest):
    try:
        save_session_summary_to_db(**session_request.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail="Couldnt save data in database")
    
    return {"status": "success", "message": "Data ingested successfully"}

