from flask import Blueprint, jsonify, request

from app.services.profile_service import get_all_profiles

profiles_bp = Blueprint("profiles_bp", __name__)


@profiles_bp.route("/profiles", methods=["GET"])
def get_profiles():
    profiles = get_all_profiles()
    return jsonify([p.to_dict() for p in profiles]), 200
