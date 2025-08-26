from tests.fixtures.profiles import TEST_PROFILE


def test_all_profiles(client, create_test_profile):
    # Send a GET request to get all the profiles in the system
    response = client.get("/profiles")

    # Asser that the response is 200 (OK)
    assert response.status_code == 200


def test_fetch_profile(client, create_test_profile):
    # Send a GET request to get all the profiles in the system
    response = client.get("/profiles/{}".format(create_test_profile.id))

    # Asser that the response is 200 (OK)
    assert response.status_code == 200


def test_profile_not_found(client):
    # Send a GET request to get all the profiles in the system
    response = client.get("/profiles/{}".format(TEST_PROFILE.get('id')))

    # Asser that the response is 200 (OK)
    assert response.status_code == 404
