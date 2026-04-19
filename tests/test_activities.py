"""
Integration tests for the Mergington High School API endpoints.

Tests cover all main endpoints:
- GET / (root redirect)
- GET /activities (list all activities)
- POST /activities/{activity_name}/signup (signup for activity)
- DELETE /activities/{activity_name}/unregister (unregister from activity)

These are happy path tests focusing on successful operations.
"""

import pytest


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_all_activities(self, test_client, sample_activities):
        """
        Test GET /activities returns all activities with correct structure.
        
        Verifies:
        - Status code is 200
        - Response contains all activities
        - Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Basketball Team"]
        
        # Act
        response = test_client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == 3
        for activity_name in expected_activities:
            assert activity_name in data
        
        # Verify activity structure
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_activities_contain_current_participants(self, test_client, sample_activities):
        """
        Test that activities include existing participants.
        
        Verifies that the Chess Club has the participant added in the fixture.
        """
        # Arrange
        activity_name = "Chess Club"
        expected_participant = "michael@mergington.edu"
        
        # Act
        response = test_client.get("/activities")
        data = response.json()
        chess_club = data[activity_name]
        
        # Assert
        assert expected_participant in chess_club["participants"]
        assert len(chess_club["participants"]) == 1


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, test_client, sample_activities):
        """
        Test GET / redirects to /static/index.html.
        
        Verifies:
        - Status code is 307 (temporary redirect)
        - Location header points to /static/index.html
        """
        # Arrange
        expected_status_code = 307
        expected_location = "/static/index.html"
        
        # Act
        response = test_client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status_code
        assert response.headers["location"] == expected_location


class TestSignupEndpoint:
    """Tests for the signup endpoint: POST /activities/{activity_name}/signup"""
    
    def test_signup_success(self, test_client, sample_activities):
        """
        Test successful signup for an activity.
        
        Verifies:
        - Status code is 200
        - Participant email is added to the activity
        - Response message is correct
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"
        signup_url = f"/activities/{activity_name}/signup"
        
        # Act
        response = test_client.post(signup_url, params={"email": email})
        data = response.json()
        
        # Assert - Response structure
        assert response.status_code == 200
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Assert - Participant was added
        activities_response = test_client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_multiple_participants(self, test_client, sample_activities):
        """
        Test signing up multiple participants to the same activity.
        
        Verifies:
        - Multiple participants can signup to the same activity
        - Each signup returns success
        """
        # Arrange
        activity_name = "Programming Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        signup_url = f"/activities/{activity_name}/signup"
        
        # Act - First signup
        response1 = test_client.post(signup_url, params={"email": email1})
        
        # Act - Second signup
        response2 = test_client.post(signup_url, params={"email": email2})
        
        # Assert - Both signups succeeded
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Assert - Both participants in activity
        activities_response = test_client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint: DELETE /activities/{activity_name}/unregister"""
    
    def test_unregister_success(self, test_client, sample_activities):
        """
        Test successful unregistration from an activity.
        
        Verifies:
        - Status code is 200
        - Participant email is removed from the activity
        - Response message is correct
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Exists in fixture
        unregister_url = f"/activities/{activity_name}/unregister"
        
        # Act
        response = test_client.delete(unregister_url, params={"email": email})
        data = response.json()
        
        # Assert - Response structure
        assert response.status_code == 200
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Assert - Participant was removed
        activities_response = test_client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_then_signup_again(self, test_client, sample_activities):
        """
        Test that a participant can signup again after unregistering.
        
        Verifies:
        - Participant can be removed and re-added to an activity
        - Activity participant list reflects the changes
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        unregister_url = f"/activities/{activity_name}/unregister"
        signup_url = f"/activities/{activity_name}/signup"
        
        # Act - Unregister
        unregister_response = test_client.delete(unregister_url, params={"email": email})
        
        # Assert - Unregister succeeded
        assert unregister_response.status_code == 200
        
        # Assert - Participant removed
        activities1 = test_client.get("/activities").json()
        assert email not in activities1[activity_name]["participants"]
        
        # Act - Signup again
        signup_response = test_client.post(signup_url, params={"email": email})
        
        # Assert - Signup succeeded
        assert signup_response.status_code == 200
        
        # Assert - Participant re-added
        activities2 = test_client.get("/activities").json()
        assert email in activities2[activity_name]["participants"]
