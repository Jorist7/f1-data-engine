from pydantic import BaseModel

class SessionRequest(BaseModel):
    year: int
    grand_prix: str
    session_type: str
    drivers: list[str]