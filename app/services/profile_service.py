from app.models import Profile


def get_all_profiles():
    profiles = Profile.query.all()
    return profiles
