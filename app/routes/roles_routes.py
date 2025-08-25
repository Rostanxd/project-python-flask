from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Role
from app.services.role_service import create, update_role_users

roles_bp = Blueprint("roles_bp", __name__)


@roles_bp.route("/roles", methods=["POST"])
def create_role():
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
def assign_users_to_role(role_id: int):
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
