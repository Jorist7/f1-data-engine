import fastf1
from app.core.database import SessionLocal
from app.models.lap_summary import LapSummary

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

def save_session_summary_to_db(year: int, grand_prix: str, session_type: str, drivers: list[str]):
    db = SessionLocal()

    try:
        summaries = get_session_summary(year, grand_prix, session_type, drivers)

        for summary in summaries:
            data = LapSummary(
                year=year,
                grand_prix=grand_prix,
                session_type=session_type,
                **summary # Entpackt die restlichen Daten
            )
            db.add(data)
        db.commit()
        print(f"Daten für {grand_prix} ({year}) erfolgreich gespeichert")

    except Exception as e:
        db.rollback()
        print(f"Fehler beim Speichern in die DB: {e}")

    finally:
        db.close()
    

    
        