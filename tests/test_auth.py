from app.models import UserStatusEnum
from tests.fixtures.users import ACTIVE_USER, TEST_USER


def test_register_user(client):
    # Send a POST request to register a new user
    response = client.post("/register", json=TEST_USER)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response JSON contains the expected message
    json_data = response.get_json()
    assert json_data["message"] == "User registered successfully"

    # Checks that the user is created with status INACTIVE by default
    assert json_data.get("user", {}).get("status", "") == UserStatusEnum.INACTIVE.value

    # Check if the profile was created as well
    assert json_data.get("user", {}).get("profile", {}).get("id", 0) != 0


def test_login_user(client, create_authenticated_user):
    client.post("/register", json=TEST_USER)

    # Prepare login data
    login_data = {
        "email": TEST_USER.get("email"),
        "password": TEST_USER.get("password"),
    }

    # Send a POST request to login
    response = client.post("/login", json=login_data)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the expected message
    json_data = response.get_json()
    assert json_data["message"] == "Login successful"
    assert json_data["token"] != ""


def test_login_invalid_user(client):
    # Prepare invalid login data
    login_data = {
        "username": "notauser",
        "email": "notauser@example.com",
        "password": "validpassword",
    }
    client.post("/register", json=login_data)

    # Send a POST request to login
    # use the wrong password to test the invalid login
    response = client.post(
        "/login", json={"email": "notauser@example.com", "password": "INvalidpassword"}
    )

    # Assert that the response status code is 401 (Unauthorized)
    assert response.status_code == 401


def test_add_role_to_user(client, auth_header, active_user, create_test_role):
    response = client.patch(
        "/user/roles",
        json={"email": active_user.email, "roles": [create_test_role.role_id]},
        headers=auth_header,
    )

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200


def test_add_role_to_not_exist_user(client, auth_header, create_test_role):
    response = client.patch(
        "/user/roles",
        json={"email": ACTIVE_USER.get("email"), "roles": [create_test_role.role_id]},
        headers=auth_header,
    )
    assert response.status_code == 404


def test_add_role_not_exist(client, auth_header, active_user):
    response = client.patch(
        "/user/roles",
        json={"email": active_user.email, "roles": [1]},
        headers=auth_header,
    )
    assert response.status_code == 400


def test_invalid_payload(client, auth_header, active_user, create_test_role):
    response = client.patch(
        "/user/roles",
        json={"email": ACTIVE_USER.get("email"), "roles": ["abc"]},
        headers=auth_header,
    )
    assert response.status_code == 400

    response = client.patch(
        "/user/roles",
        json={"email": ACTIVE_USER.get("email"), "roles": create_test_role.role_id},
        headers=auth_header,
    )
    assert response.status_code == 400
