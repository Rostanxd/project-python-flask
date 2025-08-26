def test_all_profiles(client, create_test_profile):
    # Send a GET request to get all the profiles in the system
    response = client.get("/profiles")

    # Asser that the response is 200 (OK)
    assert response.status_code == 200
