from flask import Blueprint, jsonify, request

from app.models import Role
from app.services.role_service import create

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
