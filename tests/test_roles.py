from typing_extensions import assert_type

from tests.fixtures.roles import TEST_ROLE
from tests.fixtures.users import active_user, ACTIVE_USER


def test_role_creation(client, auth_header):
    # Send a POST request to register a new role
    response = client.post("/roles", json=TEST_ROLE, headers=auth_header)

    # Assert that the response code is 201 (Created)
    assert response.status_code == 201


def test_invalid_payload(client, auth_header):
    # Send a POST request to register a new role incompleted ("department_name" is missing")
    response = client.post(
        "/roles", json={"role_name": TEST_ROLE.get("role_name")}, headers=auth_header
    )

    # Assert that the response code is 400 (Bad Request)
    assert response.status_code == 400


def test_cannot_create_duplicate_role(client, auth_header, create_test_role):
    # "Test" role was created with the fixture
    # Now we call the API to assert the error
    response = client.post("/roles", json=TEST_ROLE, headers=auth_header)

    # Assert that the response code is 400 (Bad Request)
    assert response.status_code == 400


def test_add_users(client, auth_header, create_test_role, active_user, inactive_user):
    # Send a POST request to update role's users
    response = client.post(
        "/roles/{}/users".format(create_test_role.role_id),
        json={"user_ids": [active_user.id, inactive_user.id]},
        headers=auth_header,
    )

    # Assert that the response code is 200 (OK)
    assert response.status_code == 200

    # Check if the users now belong to the role
    payload = response.get_json()
    payload_users = payload.get("users", [])

    # Check if only 2 users belong to that role
    assert len(payload_users) == 2

    # Check if the active user is part of the list
    assert any(user.get("id") == active_user.id for user in payload_users)

    # Check if the inactive user is part of the list
    assert any(user.get("id") == inactive_user.id for user in payload_users)


def test_remove_users(client, auth_header, role_with_users, active_user, inactive_user):
    # Call API removing all users from this role
    response = client.post(
        f"/roles/{role_with_users.role_id}/users",
        json={"user_ids": []},
        headers=auth_header,
    )
    assert response.status_code == 200

    # Check if the "users" key in the response is empty
    payload = response.get_json()
    assert len(payload.get("users")) == 0


def test_invalid_user_payload(client, auth_header, create_test_role, active_user):
    # Call API removing all users from this role
    response = client.post(
        f"/roles/{create_test_role.role_id}/users",
        json={"user_ids": active_user.id},
        headers=auth_header,
    )
    assert response.status_code == 400


def test_role_does_not_exist(client, auth_header):
    # Send a POST request to update role's users
    response = client.post(
        "/roles/{}/users".format(TEST_ROLE.get("id")),
        json={"user_ids": [ACTIVE_USER.get("id")]},
        headers=auth_header,
    )

    # Assert that the response code is 404 (role does not exist)
    assert response.status_code == 404


def test_invalid_user_id(client, auth_header, create_test_role):
    # Send a POST request to update role's users
    response = client.post(
        "/roles/{}/users".format(create_test_role.role_id),
        json={"user_ids": [ACTIVE_USER.get("id")]},
        headers=auth_header,
    )

    # Assert that the response code is 400 (user is not valid)
    assert response.status_code == 400
