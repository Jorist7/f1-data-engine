from pydantic import BaseModel, ConfigDict

class SessionRequest(BaseModel):
    year: int
    grand_prix: str
    session_type: str
    drivers: list[str]

class TyreDegradationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: int
    grand_prix: str
    session_type: str
    driver: str
    stint: int
    compound: str
    degradation_per_lap: float
    base_pace: float
    laps_analyzed: int