from flask import Blueprint, jsonify, request
from werkzeug.exceptions import NotFound, BadRequest
from ..services.user_service import (
    create_user,
    check_password,
    toggle_status,
    get_user_by_email,
)

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    user = create_user(username, email, password)
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


@user_bp.route("/profile", methods=["GET"])
def profile():
    # Dummy profile route for the user
    # In a real system, you would have authentication and user session handling
    return jsonify({"message": "User profile information"}), 200


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
