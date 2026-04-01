"""
Tests for the GET /activities endpoint.

Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""


def test_get_activities_success(client):
    """
    Test that the /activities endpoint returns a successful response.
    
    Arrange: TestClient is ready (from fixture)
    Act: Make GET request to /activities
    Assert: Response status is 200 and returns a dict
    """
    # Arrange
    # (client fixture provides everything we need)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0


def test_get_activities_includes_all_expected_activities(client):
    """
    Test that all 9 expected activities are present in the response.
    
    Arrange: Define expected activity names
    Act: Fetch activities from the API
    Assert: Verify all expected activities exist with proper structure
    """
    # Arrange
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball",
        "Tennis Club",
        "Drama Club",
        "Art Studio",
        "Debate Team",
        "Math Olympiad"
    ]
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name in expected_activities:
        assert activity_name in activities, f"Activity {activity_name} not found"
        activity = activities[activity_name]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


def test_get_activities_has_valid_structure(client):
    """
    Test that each activity has the expected data structure.
    
    Arrange: Make API request
    Act: Get activities response
    Assert: Verify each activity has required fields with correct types
    """
    # Arrange & Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name, details in activities.items():
        assert isinstance(activity_name, str)
        assert isinstance(details, dict)
        assert isinstance(details["description"], str)
        assert isinstance(details["schedule"], str)
        assert isinstance(details["max_participants"], int)
        assert isinstance(details["participants"], list)
        assert details["max_participants"] > 0
