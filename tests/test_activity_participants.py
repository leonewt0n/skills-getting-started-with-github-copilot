import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client_and_activities(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as client:
        yield client, test_activities


def test_signup_adds_participant(client_and_activities):
    # Arrange
    client, activities = client_and_activities

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new@mergington.edu"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new@mergington.edu for Chess Club"
    }
    assert "new@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity(client_and_activities):
    # Arrange
    client, _ = client_and_activities

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client_and_activities):
    # Arrange
    client, _ = client_and_activities

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }


def test_remove_participant_removes_existing_email(client_and_activities):
    # Arrange
    client, activities = client_and_activities

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "existing@mergington.edu"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Removed existing@mergington.edu from Chess Club"
    }
    assert "existing@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_participant_rejects_unknown_activity(client_and_activities):
    # Arrange
    client, _ = client_and_activities

    # Act
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "existing@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_rejects_unregistered_email(client_and_activities):
    # Arrange
    client, _ = client_and_activities

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "missing@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
