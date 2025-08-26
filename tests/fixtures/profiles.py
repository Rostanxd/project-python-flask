import pytest

from app.models import Profile

TEST_PROFILE = {
    "first_name": "John",
    "last_name": "Doe",
    "bio": "I am a test bio."
}


@pytest.fixture
def profile_factory(client):
    def _create_profile(user_id: int, first_name: str, last_name: str, bio: str = ""):
        app = client.application
        db = app.extensions["sqlalchemy"]
        with app.app_context():
            profile = Profile(user_id=user_id, first_name=first_name, last_name=last_name, bio=bio)
            db.session.add(profile)
            db.session.commit()
            db.session.refresh(profile)
            return profile

    return _create_profile


@pytest.fixture
def create_test_profile(profile_factory, active_user):
    return profile_factory(user_id=active_user.id, first_name=TEST_PROFILE.get('first_name'),
                           last_name=TEST_PROFILE.get('last_name'), bio=TEST_PROFILE.get('bio'))
