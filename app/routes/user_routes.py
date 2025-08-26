from flask import Blueprint, jsonify, request
from werkzeug.exceptions import NotFound, BadRequest

from ..services.profile_service import create_profile
from ..services.user_service import (
    create_user,
    check_password,
    toggle_status,
    get_user_by_email,
    get_all_users,
    user_update_roles,
)

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Create user
    user = create_user(username, email, password)

    # Create a profile for this user
    create_profile(user_id=user.id, first_name=username, last_name="", bio="")

    return jsonify({"message": "User registered successfully"}), 201


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if check_password(email, password) is True:
        return jsonify({"message": "Login successful", "email": email}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@user_bp.route("/users", methods=["GET"])
def get_users():
    users = get_all_users()
    return jsonify([u.to_dict() for u in users]), 200


@user_bp.route("/user/<int:user_id>/toggle-status", methods=["POST"])
def user_toggle_status(user_id):
    try:
        user = toggle_status(user_id)
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"id": user.id, "status": user.status.value}), 200


@user_bp.route("/user/details", methods=["GET"])
def get_user_details():
    email = request.args.get("email", type=str)
    if not email:
        raise BadRequest("Missing required query parameter: email")

    user = get_user_by_email(email)
    if user is None:
        raise NotFound("User not found")

    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "status": user.status.value if user.status else None,
            }
        ),
        200,
    )


@user_bp.route("/user/roles", methods=["PATCH"])
def update_user_roles():
    data = request.get_json()
    email = data.get("email")
    roles = data.get("roles")

    # Check if the body payload is valid
    if not email or not roles:
        return jsonify({"error": "email and roles are required"}), 400
    if not isinstance(roles, list) or len(roles) == 0:
        return jsonify({"error": "roles must be a non-empty array of numbers"}), 400

    user = get_user_by_email(email=email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        data = user_update_roles(user_id=user.id, roles=roles)
        return (
            jsonify(
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "roles": data,
                }
            ),
            200,
        )
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print("Unexpected error: {}".format(str(e)))
        return jsonify({"error": "Unexpected Error"}), 500
