from app.models import UserStatusEnum


def test_register_user(client):
    # Prepare the test data
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }

    # Send a POST request to register a new user
    response = client.post("/register", json=data)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Assert that the response JSON contains the expected message
    json_data = response.get_json()
    assert json_data["message"] == "User registered successfully"

    # Checks that the user is created with status INACTIVE by default
    user_response = client.get("/user/details?email={}".format(data["email"]))
    assert user_response.status_code == 200
    assert user_response.json["status"] == UserStatusEnum.INACTIVE.value


def test_login_user(client):
    # First, register a new user
    register_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }
    client.post("/register", json=register_data)

    # Fetch user information
    user_response = client.get("/user/details?email={}".format(register_data["email"]))

    # Now, toggle user status to ACTIVE
    client.post("/user/{}/toggle-status".format(user_response.json["id"]), json={})

    # Prepare login data
    login_data = {"email": "testuser@example.com", "password": "testpassword"}

    # Send a POST request to login
    response = client.post("/login", json=login_data)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response JSON contains the expected message
    json_data = response.get_json()
    assert json_data["message"] == "Login successful"
    assert json_data["email"] == "testuser@example.com"


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
