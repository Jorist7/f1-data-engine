from app.pipeline.ingestion import calculate_tyre_degradation

def test_calculate_tyre_degradation_valid():
    mock_stint = {
        "driver": "VER",
        "stint": 1,
        "compound": "MEDIUM",
        "tyre_age": [1, 2, 3, 4],
        "lap_times": [80.0, 80.1, 80.2, 80.3]
    }

    result = calculate_tyre_degradation(mock_stint)

    assert result["degradation_per_lap"] == 0.1
    assert result["driver"] == "VER"
    assert result["laps_analyzed"] == 4

def test_calculate_tyre_degradation_too_few_laps():
    mock_stint = {
            "driver": "VER",
            "stint": 1,
            "compound": "MEDIUM",
            "tyre_age": [1, 2,],
            "lap_times": [80.0, 80.1]
        }

    result = calculate_tyre_degradation(mock_stint)

    assert len(result) == 0