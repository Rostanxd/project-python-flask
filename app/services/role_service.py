from ..models import Role, User
from ..extensions import db


def create(role_name, department_name):
    new_role = Role(role_name=role_name, department_name=department_name)
    db.session.add(new_role)
    db.session.commit()
    return new_role


def update_role_users(role_id, user_ids):
    # Check the user_ids value
    if user_ids is None or not isinstance(user_ids, list):
        raise ValueError("user_ids must be provided as an array")

    if not all(isinstance(uid, int) for uid in user_ids):
        raise ValueError("user_ids must be an array of integers")

    # Get the role from the db
    role = db.session.get(Role, role_id)
    if role is None:
        raise ValueError("Role not found")

    # No users passed on the array of user_ids
    if len(user_ids) == 0:
        try:
            role.users = []
            db.session.commit()
            return {**role.to_dict(), "users": []}
        except Exception as e:
            db.session.rollback()
            print("Error: {}".format(str(e)))
            raise ValueError("Unexpected error")

    # Fetch users and validate existence
    users = User.query.filter(User.id.in_(user_ids)).all()
    found_ids = {u.id for u in users}
    missing_ids = [uid for uid in user_ids if uid not in found_ids]

    if missing_ids:
        raise ValueError(f"Some users not found: {missing_ids}")

    # Update role
    try:
        role.users = users
        db.session.commit()
        print(role)
        print(users)
        return {
            "role": {**role.to_dict()},
            "users": [
                {"id": u.to_dict().get("id"), "email": u.to_dict().get("email")}
                for u in users
            ],
        }
    except Exception as e:
        db.session.rollback()
        print("Error: {}".format(str(e)))
        raise ValueError("Unexpected error")
