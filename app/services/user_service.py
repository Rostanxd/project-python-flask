from datetime import datetime, timezone
from sqlalchemy import select
from werkzeug.exceptions import NotFound, BadRequest
from werkzeug.security import check_password_hash

import uuid

from ..models import User, UserStatusEnum, Role, UserRole
from ..extensions import db


def create_user(username, email, password):
    new_user = User(
        username=username, email=email, password=password, public_id=uuid.uuid4()
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user


def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    return user


def get_all_users():
    users = User.query.all()
    return users


def toggle_status(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFound("User not found")

    try:
        # Toggle the user status
        current_status = user.status
        new_status = (
            UserStatusEnum.INACTIVE
            if current_status == UserStatusEnum.ACTIVE
            else UserStatusEnum.ACTIVE
        )
        user.status = new_status

        # Update the inactive_date when the user status changes to INACTIVE
        if user.status == UserStatusEnum.INACTIVE:
            user.inactive_date = datetime.now(timezone.utc)

        db.session.commit()

        return user
    except Exception as e:
        print("User toggle status error: {}".format(str(e)))
        raise BadRequest("Unexpected error")


def check_password(email, password):
    user = User.query.filter_by(email=email).first()

    if not user:
        return False

    # User password match and the user status is ACTIVE
    if (
        check_password_hash(user.password, password)
        and user.status == UserStatusEnum.ACTIVE
    ):
        return True
    else:
        return False


def user_update_roles(user_id, roles):
    if roles is None:
        raise ValueError("roles must be provided")

    try:
        role_ids = {int(r) for r in roles}
    except (TypeError, ValueError):
        raise ValueError("roles must be an iterable of numbers")

    # Validate provided role IDs exist
    if role_ids:
        existing_rows = db.session.execute(
            select(Role.role_id).where(Role.role_id.in_(role_ids))
        ).scalars()
        existing_ids = set(existing_rows)
        missing_ids = sorted(role_ids - existing_ids)
        if missing_ids:
            raise ValueError(f"Role IDs {missing_ids} do not exist")

    # Current assignments for user
    current_links = (
        db.session.query(UserRole.role_id).filter(UserRole.user_id == user_id).all()
    )
    current_ids = {rid for (rid,) in current_links}

    to_add = role_ids - current_ids
    to_remove = current_ids - role_ids

    try:
        if to_remove:
            (
                db.session.query(UserRole)
                .filter(
                    UserRole.user_id == user_id,
                    UserRole.role_id.in_(to_remove),
                )
                .delete(synchronize_session=False)
            )

        # Add new links
        if to_add:
            db.session.add_all(
                [UserRole(user_id=user_id, role_id=rid) for rid in to_add]
            )

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    # Get the roles by user
    roles = (
        db.session.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.role_id)
            .where(UserRole.user_id == user_id)
        )
        .scalars()
        .all()
    )
    return [
        {
            "id": r.role_id,
            "role_name": r.role_name,
            "department_name": r.department_name,
        }
        for r in roles
    ]
