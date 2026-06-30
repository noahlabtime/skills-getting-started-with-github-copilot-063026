import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_list():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(result, dict)
    assert expected_activity in result
    assert isinstance(result[expected_activity]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "teststudent@example.com"
    activity_path = "/activities/Chess%20Club/signup"
    expected_message = f"Signed up {email} for Chess Club"

    # Act
    response = client.post(activity_path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == expected_message
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    email = "duplicate@example.com"
    activity_path = "/activities/Chess%20Club/signup"
    expected_detail = "Student is already signed up"

    first_response = client.post(activity_path, params={"email": email})
    assert first_response.status_code == 200

    # Act
    second_response = client.post(activity_path, params={"email": email})

    # Assert
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == expected_detail


def test_unregister_participant_removes_entry():
    # Arrange
    email = "removeme@example.com"
    signup_path = "/activities/Chess%20Club/signup"
    unregister_path = "/activities/Chess%20Club/participants"
    expected_message = f"Unregistered {email} from Chess Club"

    signup_response = client.post(signup_path, params={"email": email})
    assert signup_response.status_code == 200

    # Act
    unregister_response = client.delete(unregister_path, params={"email": email})

    # Assert
    assert unregister_response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]
    assert unregister_response.json()["message"] == expected_message


def test_unregister_missing_participant_returns_404():
    # Arrange
    unregister_path = "/activities/Chess%20Club/participants"
    expected_detail = "Participant not found"

    # Act
    response = client.delete(unregister_path, params={"email": "missing@example.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail
