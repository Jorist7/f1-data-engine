from app.core.database import Base
from sqlalchemy import Column, String, Float, Integer

class TyreDegradation(Base):
    __tablename__ = "tyre_degradation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer)
    grand_prix = Column(String)
    session_type = Column(String)
    driver = Column(String)
    stint = Column(Integer)
    compound = Column(String)
    degradation_per_lap = Column(Float)
    base_pace = Column(Float)
    laps_analyzed = Column(Integer)
    