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
    """
    Endpoint to register a new user.
    ---
    tags:
      - Users
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: JSON payload to create a new user
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: "<username>"
            email:
              type: string
              format: email
              example: "<email@example.com>"
            password:
              type: string
              format: password
              example: "<password>"
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
            user:
              type: object
              description: Newly created user object
        examples:
          application/json:
            message: "User registered successfully"
            user:
              id: 1
              username: example
              email: "<email@example.com>"
              inactive_date: "2020-01-01T00:00:00"
              profile:
                bio: ""
                created_at: "2020-01-01T00:00:00"
                first_name: Example
                id: 1
                last_name: User
                updated_at: "2020-01-01T00:00:00"
                user_id: 1
      400:
        description: Bad request (invalid or missing fields)
        schema:
          type: object
          properties:
            error:
              type: string
        examples:
          application/json:
            error: "username, email and password are required"
      500:
        description: Unexpected server error
        schema:
          type: object
          properties:
            error:
              type: string
        examples:
          application/json:
            error: "Unexpected error"
    """

    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Create user
    user = create_user(username, email, password)

    # Create a profile for this user
    create_profile(user_id=user.id, first_name=username, last_name="", bio="")

    return (
        jsonify(
            {"message": "User registered successfully", "user": {**user.to_dict()}}
        ),
        201,
    )


@user_bp.route("/login", methods=["POST"])
def login():
    """
    User login endpoint.
    ---
    tags:
      - Users
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: JSON payload with user credentials
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: "<email@example.com>"
            password:
              type: string
              format: password
              example: "<password>"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Login successful"
            email:
              type: string
              format: email
              example: "<email@example.com>"
        examples:
          application/json:
            message: "Login successful"
            email: "<email@example.com>"
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid credentials"
        examples:
          application/json:
            message: "Invalid credentials"
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if check_password(email, password) is True:
        return jsonify({"message": "Login successful", "email": email}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@user_bp.route("/users", methods=["GET"])
def get_users():
    """
    Retrieve a list of users.
    ---
    tags:
      - Users
    produces:
      - application/json
    responses:
      200:
        description: List of users
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              username:
                type: string
                example: "<username>"
              email:
                type: string
                format: email
                example: "<email@example.com>"
        examples:
          application/json:
            - id: 1
              username: "<username>"
              email: "<email@example.com>"
            - id: 2
              username: "<another_username>"
              email: "<another@example.com>"
      500:
        description: Unexpected server error
        schema:
          type: object
          properties:
            error:
              type: string
        examples:
          application/json:
            error: "Unexpected error"
    """
    users = get_all_users()
    return jsonify([u.to_dict() for u in users]), 200


@user_bp.route("/user/<int:user_id>/toggle-status", methods=["POST"])
def user_toggle_status(user_id):
    """
    Toggle a user's status.
    ---
    tags:
      - Users
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: ID of the user whose status will be toggled
    responses:
      200:
        description: Status toggled successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 123
            status:
              type: string
              description: New status after toggle
              example: "ACTIVE"
        examples:
          application/json:
            id: 123
            status: "ACTIVE"
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid request"
        examples:
          application/json:
            error: "Invalid request"
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
        examples:
          application/json:
            error: "User not found"
    """
    try:
        user = toggle_status(user_id)
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"id": user.id, "status": user.status.value}), 200


@user_bp.route("/user/details", methods=["GET"])
def get_user_details():
    """
    Get user details by email.
    ---
    tags:
      - Users
    produces:
      - application/json
    parameters:
      - in: query
        name: email
        type: string
        format: email
        required: true
        description: Email of the user to retrieve
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 123
            username:
              type: string
              example: "<username>"
            email:
              type: string
              format: email
              example: "<email@example.com>"
            status:
              type: string
              description: Current status of the user
              example: "ACTIVE"
        examples:
          application/json:
            id: 123
            username: "<username>"
            email: "<email@example.com>"
            status: "ACTIVE"
      400:
        description: Missing or invalid query parameter
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required query parameter: email"
        examples:
          application/json:
            error: "Missing required query parameter: email"
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
        examples:
          application/json:
            error: "User not found"
    """
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
    """
    Update a user's roles by email.
    ---
    tags:
      - Users
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: JSON payload containing the user's email and the new list of role IDs
        schema:
          type: object
          required:
            - email
            - roles
          properties:
            email:
              type: string
              format: email
              example: "<email@example.com>"
            roles:
              type: array
              items:
                type: integer
              example: [1, 2, 3]
    responses:
      200:
        description: Roles updated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 123
            email:
              type: string
              format: email
              example: "<email@example.com>"
            username:
              type: string
              example: "<username>"
            roles:
              type: array
              description: Updated list of role IDs
              items:
                type: object
        examples:
          application/json:
            id: 123
            email: "<email@example.com>"
            username: "<username>"
            roles: [{"id": 1, "department_name": "IT", "role_name": "DEV"}]
      400:
        description: Invalid request payload or validation error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "roles must be a non-empty array of numbers"
        examples:
          application/json:
            error: "email and roles are required"
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
        examples:
          application/json:
            error: "User not found"
      500:
        description: Unexpected server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unexpected Error"
        examples:
          application/json:
            error: "Unexpected Error"
    """
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
