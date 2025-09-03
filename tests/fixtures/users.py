import uuid
import pytest

from werkzeug.security import generate_password_hash

from app.models import User, UserStatusEnum

TEST_USER = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword",
}

ACTIVE_USER = {
    "username": "active_user",
    "email": "active@example.test",
    "status": UserStatusEnum.ACTIVE,
    "password": "testpassword",
}

INACTIVE_USER = {
    "username": "inactive_user",
    "email": "inactive@example.test",
    "status": UserStatusEnum.INACTIVE,
    "password": "testpassword",
}


@pytest.fixture
def user_factory(client):
    def _create_user(
            username: str, email: str, status: UserStatusEnum, password: str = "testpass123"
    ):
        app = client.application
        db = app.extensions["sqlalchemy"]
        hashed_password = generate_password_hash(password)
        with app.app_context():
            user = User(
                username=username, email=email, password=hashed_password, status=status, public_id=uuid.uuid4()
            )
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            return user

    return _create_user


@pytest.fixture
def create_authenticated_user(user_factory):
    return user_factory(
        TEST_USER.get("username"),
        TEST_USER.get("email"),
        UserStatusEnum.ACTIVE,
        TEST_USER.get("password")
    )


@pytest.fixture
def active_user(user_factory):
    return user_factory(
        ACTIVE_USER.get("username"),
        ACTIVE_USER.get("email"),
        ACTIVE_USER.get("status"),
        ACTIVE_USER.get("password")
    )


@pytest.fixture
def inactive_user(user_factory):
    return user_factory(
        INACTIVE_USER.get("username"),
        INACTIVE_USER.get("email"),
        INACTIVE_USER.get("status"),
        INACTIVE_USER.get("password")
    )


@pytest.fixture
def auth_header(client, create_authenticated_user):
    """
    Fixture to log in a user and provide the Authorization header
    """
    # Prepare login data
    login_data = {"email": TEST_USER.get('email'), "password": TEST_USER.get('password')}

    # Login to retrieve the token
    response = client.post("/login", json=login_data)
    token = response.get_json().get("token")

    # Return the "Authorization" header with the token
    return {"Authorization": f"Bearer {token}"}
