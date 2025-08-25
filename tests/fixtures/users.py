import pytest
from app.models import User, UserStatusEnum


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
    return user_factory("active_user", "active@example.test", UserStatusEnum.ACTIVE)


@pytest.fixture
def inactive_user(user_factory):
    return user_factory(
        "inactive_user", "inactive@example.test", UserStatusEnum.INACTIVE
    )
