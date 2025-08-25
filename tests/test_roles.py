from tests.fixtures.roles import TEST_ROLE


def test_role_creation(client):
    # Send a POST request to register a new role
    response = client.post("/roles", json=TEST_ROLE)

    # Assert that the response code is 201 (Created)
    assert response.status_code == 201


def test_invalid_payload(client):
    # Send a POST request to register a new role incompleted ("department_name" is missing")
    response = client.post("/roles", json={"role_name": TEST_ROLE.get("role_name")})

    # Assert that the response code is 400 (Bad Request)
    assert response.status_code == 400


def test_cannot_create_duplicate_role(client, create_test_role):
    # "Test" role was created with the fixture
    # Now we call the API to assert the error
    response = client.post("/roles", json=TEST_ROLE)

    # Assert that the response code is 400 (Bad Request)
    assert response.status_code == 400
