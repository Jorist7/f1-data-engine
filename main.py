from fastapi import FastAPI, HTTPException, Depends
from app.core.database import SessionLocal, init_db
from app.models.lap_summary import LapSummary
from app.models.tyre_degradation import TyreDegradation
from sqlalchemy.orm import Session
from app.models.pydantic_models import SessionRequest
from app.pipeline.ingestion import save_session_summary_to_db, save_degradation_to_db, get_stint_telemetry, calculate_tyre_degradation

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
def fetch_session(session_request: SessionRequest, db: Session = Depends(get_db)):
    try:
        save_session_summary_to_db(db=db, **session_request.model_dump())
    except Exception:
        raise HTTPException(status_code=400, detail="Couldnt save data in database")
    
    return {"status": "success", "message": "Data ingested successfully"}

@app.get("/degradation/{year}/{grand_prix}/{session_type}/{driver}/{stint}")
def get_degradation_data(year: int, grand_prix: str, session_type: str, driver: str, stint: int, db: Session = Depends(get_db)):
    degradation_data = db.query(TyreDegradation).filter(
        TyreDegradation.year == year,
        TyreDegradation.grand_prix == grand_prix,
        TyreDegradation.session_type == session_type,
        TyreDegradation.driver == driver,
        TyreDegradation.stint == stint
    ).first()

    if degradation_data:
        return {"degradation_data": degradation_data}

    stint_telemetry = get_stint_telemetry(year, grand_prix, session_type, driver, stint)
    tyre_degradation = calculate_tyre_degradation(stint_telemetry)

    if not tyre_degradation:
        raise HTTPException(status_code=404, detail="No valid stint telemetry or degradation data found!")

    saved_data = save_degradation_to_db(tyre_degradation, db)

    if not saved_data:
        raise HTTPException(status_code=500, detail="Could not save degradation data to database!")

    return {"degradation_data": saved_data}



