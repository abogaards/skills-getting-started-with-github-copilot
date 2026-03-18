import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities():
    # Arrange
    # (State reset automatically)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload


def test_signup_for_activity_success():
    # Arrange
    email = "new_student@example.com"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_duplicate():
    # Arrange
    existing = activities["Chess Club"]["participants"][0]

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": existing})

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_activity_full():
    # Arrange
    activity = activities["Chess Club"]
    activity["participants"] = [f"p{i}@example.com" for i in range(activity["max_participants"])]

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "extra_student@example.com"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_from_activity_success():
    # Arrange
    email = activities["Chess Club"]["participants"][0]

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_from_activity_participant_missing():
    # Arrange
    missing_email = "missing@example.com"

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_from_activity_not_found():
    # Arrange
    # Act
    response = client.delete("/activities/DoesNotExist/participants", params={"email": "x@example.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"