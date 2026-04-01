"""
Tests for the DELETE /activities/{activity_name}/unregister endpoint.

Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""


def test_unregister_success(client):
    """
    Test that a registered student can successfully unregister from an activity.
    
    Arrange: Use a student already registered for an activity
    Act: Send DELETE request to unregister endpoint
    Assert: Response is 200 and success message is returned
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered
    
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_unregister_removes_participant_from_activity(client):
    """
    Test that unregister actually removes the student from the participants list.
    
    Arrange: Note initial participant count and participant in list
    Act: Send unregister request and fetch updated activities
    Assert: Verify participant count decreased and email is no longer in list
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity_name]["participants"]
    initial_count = len(initial_participants)
    
    # Act
    client.delete(f"/activities/{activity_name}/unregister?email={email}")
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    updated_count = len(updated_participants)
    
    # Assert
    assert updated_count == initial_count - 1
    assert email not in updated_participants


def test_unregister_activity_not_found(client):
    """
    Test that unregister returns 404 when activity doesn't exist.
    
    Arrange: Define a non-existent activity name
    Act: Attempt to unregister from non-existent activity
    Assert: Response is 404 with "Activity not found" message
    """
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_registered(client):
    """
    Test that unregister returns 400 when student is not registered.
    
    Arrange: Use an email not registered for the activity
    Act: Attempt to unregister a non-registered student
    Assert: Response is 400 with appropriate error message
    """
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not registered for this activity"


def test_unregister_then_signup_again(client):
    """
    Test that a student can unregister and then sign up again for the same activity.
    
    Arrange: Prepare activity and student email
    Act: Unregister student, then sign them up again
    Assert: Both operations succeed, student is in participant list at the end
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act - unregister
    unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert unregister succeeded
    assert unregister_response.status_code == 200
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
    
    # Act - sign up again
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert signup succeeded
    assert signup_response.status_code == 200
    final_activities = client.get("/activities").json()
    assert email in final_activities[activity_name]["participants"]


def test_unregister_multiple_times_fails(client):
    """
    Test that unregistering the same student twice fails.
    
    Arrange: Prepare to unregister a student
    Act: Unregister student once (succeeds), then try again (should fail)
    Assert: First unregister is 200, second is 400
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act & Assert - first unregister
    response1 = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response1.status_code == 200
    
    # Act & Assert - second unregister (should fail)
    response2 = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Student not registered for this activity"


def test_unregister_doesnt_affect_other_activities(client):
    """
    Test that unregistering from one activity doesn't affect participant lists in others.
    
    Arrange: Sign up student for two activities
    Act: Unregister from first activity
    Assert: Student is removed from first, still in second
    """
    # Arrange
    student_email = "multi@mergington.edu"
    activity1 = "Chess Club"
    activity2 = "Programming Class"
    
    # Sign up for both activities
    client.post(f"/activities/{activity1}/signup?email={student_email}")
    client.post(f"/activities/{activity2}/signup?email={student_email}")
    
    # Act - unregister from first activity
    response = client.delete(f"/activities/{activity1}/unregister?email={student_email}")
    
    # Assert
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert student_email not in activities[activity1]["participants"]
    assert student_email in activities[activity2]["participants"]
