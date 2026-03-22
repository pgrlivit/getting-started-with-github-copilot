import pytest


class TestGetActivities:
    def test_get_activities_success(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data


class TestSignupForActivity:
    def test_signup_success(self, reset_activities):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = reset_activities.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity}"
        
        # Verify participant was added
        activities_response = reset_activities.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]
    
    def test_signup_duplicate_registration(self, reset_activities):
        """Test that duplicate signup is rejected"""
        email = "michael@mergington.edu"  # Already registered
        activity = "Chess Club"
        
        response = reset_activities.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_activity_not_found(self, reset_activities):
        """Test signup for non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = reset_activities.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_capacity_check(self, reset_activities):
        """Test that we can add participants up to max capacity"""
        activity = "Tennis Club"  # max_participants: 10
        activities_response = reset_activities.get("/activities")
        activities = activities_response.json()
        current_count = len(activities[activity]["participants"])
        
        # Should be able to add participants up to max
        email = f"newstudent{current_count}@mergington.edu"
        response = reset_activities.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200


class TestUnregisterFromActivity:
    def test_unregister_success(self, reset_activities):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already registered in Chess Club
        activity = "Chess Club"
        
        response = reset_activities.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity}"
        
        # Verify participant was removed
        activities_response = reset_activities.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]
    
    def test_unregister_not_signed_up(self, reset_activities):
        """Test unregistering from activity when not signed up"""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = reset_activities.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_activity_not_found(self, reset_activities):
        """Test unregistering from non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = reset_activities.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_unregister_already_unregistered(self, reset_activities):
        """Test unregistering twice from same activity"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # First unregister - should succeed
        response1 = reset_activities.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Second unregister - should fail
        response2 = reset_activities.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response2.status_code == 400
