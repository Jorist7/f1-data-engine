import pytest
from app.core.database import Base
from app.models.lap_summary import LapSummary
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Vorbereiten der Testdatenbank
@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

def test_get_lap_summaries_empty(client):
    response = client.get("/lap-summaries")
    assert response.status_code == 404
    assert response.json() == {"detail": "No results found!"}

def test_get_lap_summaries_with_data(client):
    db = TestingSessionLocal()
    test_data = LapSummary(
        year=2025,
        grand_prix="Monaco",
        session_type="Q",
        driver="NOR",
        lap_time_formatted="1:11.345",
        top_speed=295.4,
        sector_1=18.123,
        sector_2=32.456,
        sector_3=20.766
    )
    db.add(test_data)
    db.commit()
    db.close()

    response = client.get("/lap-summaries?driver=NOR")

    assert response.status_code == 200
    data = response.json()
    assert len(data["summaries"]) == 1
    assert data["summaries"][0]["driver"] == "NOR"
    assert data["summaries"][0]["grand_prix"] == "Monaco"





