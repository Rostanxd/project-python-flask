from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Profile

from app.services.profile_service import get_all_profiles, update_profile_data

profiles_bp = Blueprint("profiles_bp", __name__)


@profiles_bp.route("/profiles", methods=["GET"])
def get_profiles():
    """
    Retrieve a list of profiles.
    ---
    tags:
      - Profiles
    produces:
      - application/json
    responses:
      200:
        description: List of profiles
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              first_name:
                type: string
                example: "<first name>"
              last_name:
                type: string
                example: "<last name>"
              bio:
                type: string
                example: "<short bio>"
              user_id:
                type: integer
                example: 42
              user:
                type: object
                properties:
                  email:
                    type: string
                    example: "example@example.com"
                  id:
                    type: integer
                    example: 1
                  inactive_date:
                    type: string
                    example: "2020-01-01T00:00:00"
                  roles:
                    type: array
                    example: []
                  status:
                    type: string
                    example: "ACTIVE"
                  username:
                    type: string
                    example: "example"
        examples:
          application/json:
            - id: 1
              first_name: "<first name>"
              last_name: "<last name>"
              bio: "<short bio>"
              user_id: 42
              user:
                email: "email@example.com"
                id: 1
                inactive_date: "2020-01-01T00:00:00"
                roles: []
                status: "ACTIVE"
                username: "example"
            - id: 2
              first_name: "<another name>"
              last_name: "<another name>"
              bio: "<another short bio>"
              user_id: 77
              user:
                email: "another@example.com"
                id: 2
                inactive_date: "2020-01-01T00:00:00"
                roles: []
                status: "ACTIVE"
                username: "another"
      500:
        description: Unexpected server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unexpected error"
    """
    profiles = get_all_profiles()
    return jsonify([p.to_dict() for p in profiles]), 200


@profiles_bp.route("/profiles/<int:profile_id>", methods=["GET"])
def get_profile(profile_id: int):
    """
    Retrieve a profile by ID.
    ---
    tags:
      - Profiles
    produces:
      - application/json
    parameters:
      - in: path
        name: profile_id
        type: integer
        required: true
        description: ID of the profile to retrieve
    responses:
      200:
        description: Profile details
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            first_name:
              type: string
              example: "<first name>"
            last_name:
              type: string
              example: "<last name>"
            bio:
              type: string
              example: "<short bio>"
            user_id:
              type: integer
              example: 42
            user:
              type: object
              properties:
                email:
                  type: string
                  example: "example@example.com"
                id:
                  type: integer
                  example: 1
                inactive_date:
                  type: string
                  example: "2020-01-01T00:00:00"
                roles:
                  type: array
                  example: []
                status:
                  type: string
                  example: "ACTIVE"
                username:
                  type: string
                  example: "example"
        examples:
          application/json:
            id: 1
            first_name: "<first name>"
            last_name: "<last name>"
            bio: "<short bio>"
            user_id: 42
            user:
              email: "email@example.com"
              id: 1
              inactive_date: "2020-01-01T00:00:00"
              roles: []
              status: "ACTIVE"
              username: "example"
      404:
        description: Profile not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Profile not found"
        examples:
          application/json:
            error: "Profile not found"
    """
    # Get the profile from the db
    profile = db.session.get(Profile, profile_id)

    if profile is None:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify(profile.to_dict()), 200


@profiles_bp.route("/profiles/<int:profile_id>", methods=["PATCH"])
def update_profile(profile_id: int):
    """
    Update a profile by ID.
    ---
    tags:
      - Profiles
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: path
        name: profile_id
        type: integer
        required: true
        description: ID of the profile to update
      - in: body
        name: body
        required: true
        description: JSON payload with fields to update. At least one field is required.
        schema:
          type: object
          properties:
            first_name:
              type: string
              example: "<first name>"
            last_name:
              type: string
              example: "<last name>"
            bio:
              type: string
              example: "<short bio>"
    responses:
      200:
        description: Profile updated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            first_name:
              type: string
              example: "<first name>"
            last_name:
              type: string
              example: "<last name>"
            bio:
              type: string
              example: "<short bio>"
            user_id:
              type: integer
              example: 42
            user:
              type: object
              properties:
                email:
                  type: string
                  example: "example@example.com"
                id:
                  type: integer
                  example: 1
                inactive_date:
                  type: string
                  example: "2020-01-01T00:00:00"
                roles:
                  type: array
                  example: []
                status:
                  type: string
                  example: "ACTIVE"
                username:
                  type: string
                  example: "example"
      400:
        description: Invalid request payload
        schema:
          type: object
          properties:
            error:
              type: string
              example: "At least one of first_name, last_name, or bio is required"
      404:
        description: Profile not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Profile not found"
      500:
        description: Unexpected server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to update profile"
    """
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
