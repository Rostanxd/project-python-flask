from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Profile

from app.services.profile_service import get_all_profiles, update_profile_data

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


@profiles_bp.route("/profiles/<int:profile_id>", methods=["PATCH"])
def update_profile(profile_id: int):
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    bio = data.get("bio")

    # Get the profile from the db
    profile = db.session.get(Profile, profile_id)

    if profile is None:
        return jsonify({"error": "Profile not found"}), 404

    try:
        profile = update_profile_data(
            profile_id=profile_id, first_name=first_name, last_name=last_name, bio=bio
        )
        return jsonify(profile.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        print("Unexpected error: {}".format(str(e)))
        return jsonify({"error": "Failed to update profile"}), 500
