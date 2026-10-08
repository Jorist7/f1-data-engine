from app.core.database import Base
from sqlalchemy import Column, Integer, String, Float

class LapSummary(Base):
    __tablename__ = "lap_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer)
    grand_prix = Column(String)
    session_type = Column(String)
    driver = Column(String)
    lap_time_formatted = Column(String)
    top_speed = Column(Float)
    sector_1 = Column(Float)
    sector_2 = Column(Float)
    sector_3 = Column(Float)
