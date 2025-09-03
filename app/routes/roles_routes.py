from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Role
from app.services.role_service import create, update_role_users

from ..utils.token import verify_token

roles_bp = Blueprint("roles_bp", __name__)


@roles_bp.route("/roles", methods=["POST"])
@verify_token
def create_role(_):
    """
    Create a new role.
    ---
    tags:
      - Roles
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: JSON payload to create a role
        schema:
          type: object
          required:
            - role_name
            - department_name
          properties:
            role_name:
              type: string
              example: "<role name>"
            department_name:
              type: string
              example: "<department name>"
    responses:
      201:
        description: Role created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Roles created successfully"
            role:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                role_name:
                  type: string
                  example: "<role name>"
                department_name:
                  type: string
                  example: "<department name>"
      400:
        description: Invalid payload or duplicate role
        schema:
          type: object
          properties:
            error:
              type: string
              example: "role_name and department_name are required"
      500:
        description: Unexpected server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unexpected error"
    """
    data = request.get_json()
    role_name = data.get("role_name")
    department_name = data.get("department_name")

    if not role_name or not department_name:
        return jsonify({"error": "role_name and department_name are required"}), 400

    # Check for duplicate: same role_name + department_name
    existing = Role.query.filter_by(
        role_name=role_name, department_name=department_name
    ).first()

    # Returns a 400 because the role already exists for that department
    if existing:
        return jsonify({"error": "Role already exists for this department"}), 400

    # Create the role
    try:
        role = create(role_name=role_name, department_name=department_name)
        role_payload = (
            role
            if isinstance(role, dict)
            else {
                "id": getattr(role, "role_id", None),
                "role_name": getattr(role, "role_name", None),
                "department_name": getattr(role, "department_name", None),
            }
        )
        return (
            jsonify({"message": "Roles created successfully", "role": role_payload}),
            201,
        )
    except Exception:
        return jsonify({"error": "Unexpected error"}), 500


@roles_bp.route("/roles/<int:role_id>/users", methods=["POST"])
@verify_token
def assign_users_to_role(_, role_id: int):
    """
    Assign users to a role.
    ---
    tags:
      - Roles
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: path
        name: role_id
        type: integer
        required: true
        description: ID of the role to update
      - in: body
        name: body
        required: true
        description: JSON payload with user IDs to assign
        schema:
          type: object
          required:
            - user_ids
          properties:
            user_ids:
              type: array
              items:
                type: integer
              example: [1, 2, 3]
    responses:
      200:
        description: Role updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Role updated successfully"
            role:
              type: object
              properties:
                department_name:
                  type: string
                  example: "IT"
                role_id:
                  type: integer
                  example: 1
                role_name:
                  type: string
                  example: "DEV"
            users:
              type: array
              items:
                type: object
                properties:
                  email:
                    type: string
                    example: "user@example.com"
                  id:
                    type: integer
                    example: 1
      400:
        description: Invalid payload
        schema:
          type: object
          properties:
            error:
              type: string
              example: "user_ids must be a non-empty list of positive integers"
      404:
        description: Role not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Role not found"
      500:
        description: Unexpected server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unexpected Error"
    """
    data = request.get_json(silent=True) or {}
    user_ids = data.get("user_ids")

    # Get the role from the db
    role = db.session.get(Role, role_id)
    if role is None:
        return jsonify({"error": "Role not found"}), 404

    try:
        updated_role = update_role_users(role_id=role_id, user_ids=user_ids)
        return jsonify({"message": "Role updated successfully", **updated_role}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print("Unexpected error: {}".format(str(e)))
        return jsonify({"error": "Unexpected Error"}), 500
