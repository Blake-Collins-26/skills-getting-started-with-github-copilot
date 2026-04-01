"""
Tests for the POST /activities/{activity_name}/signup endpoint.

Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""


def test_signup_success(client):
    """
    Test that a new student can successfully sign up for an activity.
    
    Arrange: Define activity and new student email
    Act: Send POST request to signup endpoint
    Assert: Response is 200 and success message is returned
    """
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_adds_participant_to_activity(client):
    """
    Test that signup actually adds the student to the participants list.
    
    Arrange: Note initial participant count, prepare signup request
    Act: Send signup request and fetch updated activities
    Assert: Verify participant count increased and email is in the list
    """
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity_name]["participants"]
    initial_count = len(initial_participants)
    
    # Act
    client.post(f"/activities/{activity_name}/signup?email={email}")
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    updated_count = len(updated_participants)
    
    # Assert
    assert updated_count == initial_count + 1
    assert email in updated_participants


def test_signup_activity_not_found(client):
    """
    Test that signup returns 404 when activity doesn't exist.
    
    Arrange: Define a non-existent activity name
    Act: Attempt to sign up for non-existent activity
    Assert: Response is 404 with "Activity not found" message
    """
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_fails(client):
    """
    Test that a student cannot sign up for the same activity twice.
    
    Arrange: Use an email that's already registered for Chess Club
    Act: Attempt to sign up with duplicate email
    Assert: Response is 400 with "Student already signed up" message
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered in Chess Club
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_activity_full_fails(client):
    """
    Test that signup fails when activity reaches max participants.
    
    Arrange: Find or create an activity at capacity, prepare signup
    Act: Attempt to sign up for a full activity
    Assert: Response is 400 with "Activity is full" message
    """
    # Arrange - Use Gym Class which has more capacity, so we'll fill it
    activity_name = "Gym Class"
    initial_response = client.get("/activities")
    activity = initial_response.json()[activity_name]
    max_participants = activity["max_participants"]
    current_count = len(activity["participants"])
    
    # Sign up students until the activity is at capacity
    for i in range(max_participants - current_count):
        client.post(f"/activities/{activity_name}/signup?email=student{i}@test.edu")
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=overflow@test.edu")
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_same_student_different_activities(client):
    """
    Test that a student can sign up for multiple different activities.
    
    Arrange: Choose two different activities and same student email
    Act: Sign up student for both activities
    Assert: Both signups succeed, student appears in both activity lists
    """
    # Arrange
    student_email = "multi@mergington.edu"
    activity1 = "Chess Club"
    activity2 = "Programming Class"
    
    # Act
    response1 = client.post(f"/activities/{activity1}/signup?email={student_email}")
    response2 = client.post(f"/activities/{activity2}/signup?email={student_email}")
    
    # Assert signup responses
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Assert student is in both activity lists
    activities = client.get("/activities").json()
    assert student_email in activities[activity1]["participants"]
    assert student_email in activities[activity2]["participants"]
