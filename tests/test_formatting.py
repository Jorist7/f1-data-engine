import pytest
from app.pipeline.ingestion import format_laptime

def test_format_laptime_standard():
    assert format_laptime(75.123) == "1:15.123"

def test_format_laptime_sub_minute():
    assert format_laptime(59.999) == "0:59.999"
