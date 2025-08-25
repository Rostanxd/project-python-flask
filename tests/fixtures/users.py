import pytest
from app.models import User, UserStatusEnum


ACTIVE_USER = {
    "username": "active_user",
    "email": "active@example.test",
    "status": UserStatusEnum.ACTIVE,
}

INACTIVE_USER = {
    "username": "inactive_user",
    "email": "inactive@example.test",
    "status": UserStatusEnum.INACTIVE,
}


@pytest.fixture
def user_factory(client):
    def _create_user(
        username: str, email: str, status: UserStatusEnum, password: str = "testpass123"
    ):
        app = client.application
        db = app.extensions["sqlalchemy"]
        with app.app_context():
            user = User(
                username=username, email=email, password=password, status=status
            )
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            return user

    return _create_user


@pytest.fixture
def active_user(user_factory):
    return user_factory(
        ACTIVE_USER.get("username"), ACTIVE_USER.get("email"), ACTIVE_USER.get("status")
    )


@pytest.fixture
def inactive_user(user_factory):
    return user_factory(
        INACTIVE_USER.get("username"),
        INACTIVE_USER.get("email"),
        INACTIVE_USER.get("status"),
    )
