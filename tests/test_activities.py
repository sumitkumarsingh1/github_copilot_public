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
        response = test_client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all activities are returned
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball Team" in data
        
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
        response = test_client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
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
        response = test_client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


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
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"
        
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the participant was actually added
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
        activity_name = "Programming Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # First signup
        response1 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        assert response1.status_code == 200
        
        # Second signup
        response2 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        assert response2.status_code == 200
        
        # Verify both are in the activity
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
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # This participant exists in fixture
        
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the participant was actually removed
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
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Unregister
        unregister_response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify removed
        activities1 = test_client.get("/activities").json()
        assert email not in activities1[activity_name]["participants"]
        
        # Signup again
        signup_response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify back in activity
        activities2 = test_client.get("/activities").json()
        assert email in activities2[activity_name]["participants"]
