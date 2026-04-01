import pytest
from fastapi.testclient import TestClient
from src.app import app, create_activities_db


@pytest.fixture
def test_app():
    """
    Fixture that creates a fresh app instance with isolated database for each test.
    
    This ensures test isolation by resetting the activities database before each test
    and restoring it after the test completes.
    """
    # Store original activities
    from src import app as app_module
    original_activities = app_module.activities.copy()
    
    # Reset activities to fresh state
    app_module.activities = create_activities_db()
    
    yield app
    
    # Restore original state after test
    app_module.activities = original_activities


@pytest.fixture
def client(test_app):
    """
    Fixture that provides a TestClient with isolated database for testing the API.
    
    Uses the test_app fixture to ensure each test gets a fresh database state.
    """
    return TestClient(test_app)
