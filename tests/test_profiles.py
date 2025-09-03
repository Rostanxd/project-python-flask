from tests.fixtures.profiles import TEST_PROFILE


def test_all_profiles(client, auth_header, create_test_profile):
    # Send a GET request to get all the profiles in the system
    response = client.get("/profiles", headers=auth_header)

    # Asser that the response is 200 (OK)
    assert response.status_code == 200


def test_fetch_profile(client, auth_header, create_test_profile):
    # Send a GET request to get all the profiles in the system
    response = client.get("/profiles/{}".format(create_test_profile.id), headers=auth_header)

    # Asser that the response is 200 (OK)
    assert response.status_code == 200


def test_profile_not_found(client, auth_header):
    # Send a GET request to get all the profiles in the system
    response = client.get("/profiles/1", headers=auth_header)

    # Asser that the response is 404 (OK)
    assert response.status_code == 404


def test_update_profile(client, auth_header, create_test_profile):
    # Send a GET request to get all the profiles in the system
    response = client.patch(
        "/profiles/{}".format(create_test_profile.id),
        json={"first_name": "John", "last_name": "Doe", "bio": "I am a test bio!"},
        headers=auth_header,
    )

    # Asser that the response is 200 (OK)
    assert response.status_code == 200


def test_update_profile_not_found(client, auth_header):
    # Send a GET request to get all the profiles in the system
    response = client.patch(
        "/profiles/1",
        json={"first_name": "John", "last_name": "Doe", "bio": "I am a test bio!"},
        headers=auth_header
    )

    # Asser that the response is 404 (profile not found)
    assert response.status_code == 404
