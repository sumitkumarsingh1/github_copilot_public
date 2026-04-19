"""
Pytest configuration and shared fixtures for FastAPI tests.

Provides test client and sample activities data for integration testing.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture(scope="session")
def test_client():
    """
    Provide a TestClient for the FastAPI app.
    
    Scope: session - created once per test run as the app is immutable.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def sample_activities():
    """
    Provide a fresh copy of sample activities for each test.
    
    Modifies the app's activities dictionary to ensure clean state per test.
    Scope: function - resets after each test to prevent cross-test pollution.
    
    Yields:
        dict: A dictionary of test activities
    """
    from src.app import activities
    
    original_activities = activities.copy()
    
    # Reset to default state with fewer participants for easier testing
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Basketball Team": {
            "description": "Join the competitive basketball team and compete in regional tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
    })
    
    yield activities
    
    # Restore original state after test completes
    activities.clear()
    activities.update(original_activities)
