from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Profile

from app.services.profile_service import get_all_profiles

profiles_bp = Blueprint("profiles_bp", __name__)


@profiles_bp.route("/profiles", methods=["GET"])
def get_profiles():
    profiles = get_all_profiles()
    return jsonify([p.to_dict() for p in profiles]), 200

@profiles_bp.route("/profiles/<int:profile_id>", methods=["GET"])
def get_profile(profile_id: int):
    # Get the profile from the db
    profile = db.session.get(Profile, profile_id)

    if profile is None:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify(profile.to_dict()), 200