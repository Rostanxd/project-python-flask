from typing import Optional
from sqlalchemy.exc import SQLAlchemyError

from app.models import db, Profile


def get_all_profiles():
    profiles = Profile.query.all()
    return profiles


def update_profile_data(
        profile_id: int,
        first_name: Optional[str],
        last_name: Optional[str],
        bio: Optional[str],
):
    profile = db.session.get(Profile, profile_id)
    if profile is None:
        raise ValueError(f"Profile not found for id={profile_id}")

    try:
        if first_name is not None:
            profile.first_name = first_name
        if last_name is not None:
            profile.last_name = last_name
        if bio is not None:
            profile.bio = bio

        db.session.commit()
        db.session.refresh(profile)
        return profile
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise exc
