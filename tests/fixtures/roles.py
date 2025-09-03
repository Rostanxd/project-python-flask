import pytest
from app.models import Role

TEST_ROLE = {
    "role_name": "test_role",
    "department_name": "test_department",
}


@pytest.fixture
def role_factory(client):
    def _create_role(role_name: str, department_name: str):
        app = client.application
        db = app.extensions["sqlalchemy"]
        with app.app_context():
            role = Role(role_name=role_name, department_name=department_name)
            db.session.add(role)
            db.session.commit()
            db.session.refresh(role)
            return role

    return _create_role


@pytest.fixture
def create_test_role(role_factory):
    return role_factory(TEST_ROLE.get("role_name"), TEST_ROLE.get("department_name"))


@pytest.fixture
def role_with_users(client, auth_header, create_test_role, active_user, inactive_user):
    """
    Creates a role and links both the active and inactive users to it.
    Returns the role object (with role_id).
    """
    response = client.post(
        f"/roles/{create_test_role.role_id}/users",
        json={"user_ids": [active_user.id, inactive_user.id]},
        headers=auth_header
    )
    return create_test_role
