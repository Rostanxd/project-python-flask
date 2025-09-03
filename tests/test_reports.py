from app.models import UserStatusEnum


def test_check_all_users(client, auth_header, active_user, inactive_user):
    resp = client.get("/users", headers=auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)

    active_users = 0
    inactive_users = 0

    for user in data:
        if user.get("status") == UserStatusEnum.ACTIVE.value:
            active_users += 1
        else:
            inactive_users += 1

    assert active_users >= 1
    assert inactive_users >= 1
