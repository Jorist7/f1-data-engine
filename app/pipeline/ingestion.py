import fastf1
from app.core.database import SessionLocal
from app.models.lap_summary import LapSummary
from app.models.tyre_degradation import TyreDegradation
import numpy as np
from sqlalchemy.orm import Session

fastf1.Cache.enable_cache("data/cache")

def format_laptime(laptime: float) -> str:
    minutes = int(laptime / 60)
    seconds = laptime % 60

    return f"{minutes}:{seconds:06.3f}"

def get_driver_lap_summary(session, driver: str) -> dict:
    fastest_lap = session.laps.pick_drivers(driver).pick_fastest()
    formatted_laptime = format_laptime(fastest_lap["LapTime"].total_seconds())

    telemetry = fastest_lap.get_telemetry()
    top_speed = telemetry["Speed"].max()

    sector_1 = round(fastest_lap["Sector1Time"].total_seconds(), 3)
    sector_2 = round(fastest_lap["Sector2Time"].total_seconds(), 3)
    sector_3 = round(fastest_lap["Sector3Time"].total_seconds(), 3)

    lap_summary = {
        "driver": driver,
        "lap_time_formatted": formatted_laptime,
        "top_speed": top_speed,
        "sector_1": sector_1,
        "sector_2": sector_2,
        "sector_3": sector_3
    }

    return lap_summary

def get_session_summary(year: int, grand_prix: str, session_type: str, drivers: list[str]) -> list[dict]:
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load()
    return [get_driver_lap_summary(session, driver) for driver in drivers]

def save_session_summary_to_db(year: int, grand_prix: str, session_type: str, drivers: list[str], db: Session):
    try:
        summaries = get_session_summary(year, grand_prix, session_type, drivers)

        for summary in summaries:
            data = LapSummary(
                year=year,
                grand_prix=grand_prix,
                session_type=session_type,
                **summary
            )
            db.add(data)
        db.commit()
        print(f"Daten für {grand_prix} ({year}) erfolgreich gespeichert")

    except Exception as e:
        db.rollback()
        print(f"Error saving to database: {e}")

    finally:
        db.close()


def get_stint_telemetry(year: int, grand_prix: str, session_type: str, driver: str, stint_number: int) -> dict:
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load()

    laps = session.laps

    # Filtert die Tabelle nach den entsprechenden Bedingungen
    driver_laps = laps[
        (laps["Driver"] == driver)
        & (laps["Stint"] == stint_number)
        & (laps["IsAccurate"] == True)
    ]

    if driver_laps.empty:
        return {}

    compound = driver_laps["Compound"].iloc[0]
    tyre_age = driver_laps["TyreLife"].tolist()
    lap_times_sec = driver_laps["LapTime"].dt.total_seconds().round(3).tolist()

    return {
        "year": year,
        "grand_prix": grand_prix,
        "session_type": session_type,
        "driver": driver,
        "stint": stint_number,
        "compound": str(compound),
        "tyre_age": tyre_age,
        "lap_times": lap_times_sec
    }


def calculate_tyre_degradation(stint_data: dict) -> dict:
    if not stint_data or len(stint_data.get("tyre_age", [])) < 3:
        return {}

    tyre_age = stint_data["tyre_age"]
    lap_times = stint_data["lap_times"]

    # Lineare Regresion berechnen 
    # Slope = Steigung
    # intercept = thoertische Rundenzeit bei 0
    slope, intercept = np.polyfit(tyre_age, lap_times, 1)

    return {
        "year": stint_data["year"],
        "grand_prix": stint_data["grand_prix"],
        "session_type": stint_data["session_type"],
        "driver": stint_data["driver"],
        "stint": stint_data["stint"],
        "compound": stint_data["compound"],
        "degradation_per_lap": round(float(slope), 3),
        "base_pace": round(float(intercept), 3),
        "laps_analyzed": len(tyre_age)
    }

def save_degradation_to_db(degrad_data: dict, db: Session):
    try:
        db_entry = TyreDegradation(**degrad_data)
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)

        return db_entry

    except Exception as e:
        db.rollback()
        print(f"Error saving to database: {e}")
        return None


    


    

    
        