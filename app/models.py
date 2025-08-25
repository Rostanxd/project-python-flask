# python
import enum
from enum import Enum
from app.extensions import db, bcrypt
from sqlalchemy import inspect as sa_inspect


class UserStatusEnum(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    status = db.Column(
        db.Enum(UserStatusEnum), nullable=False, default=UserStatusEnum.INACTIVE
    )
    inactive_date = db.Column(db.DateTime, nullable=True)

    # Many-to-many via association table
    roles = db.relationship("Role", secondary="users_roles", back_populates="users")

    def to_dict(self):
        # Serialize columns, excluding sensitive ones
        data = {}
        mapper = sa_inspect(self.__class__)
        for column in mapper.columns:
            key = column.key
            if key == "password":
                continue
            value = getattr(self, key)
            # Enum to value
            if isinstance(value, enum.Enum):
                value = value.value
            # Datetime to ISO-8601, if applicable
            if hasattr(value, "isoformat"):
                try:
                    value = value.isoformat()
                except Exception:
                    pass
            data[key] = value

        # Serialize roles
        data["roles"] = [
            {
                "role_id": r.role_id,
                "role_name": r.role_name,
                "department_name": r.department_name,
            }
            for r in self.roles
        ]
        return data

    def __repr__(self):
        return f"<User {self.username}>"


class Role(db.Model):
    __tablename__ = "roles"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(80), nullable=False)
    department_name = db.Column(db.String(80), nullable=False)

    # Reciprocal side of the many-to-many
    users = db.relationship("User", secondary="users_roles", back_populates="roles")

    __table_args__ = (
        db.UniqueConstraint(
            "role_name", "department_name", name="uq_role_name_department"
        ),
    )

    def __repr__(self):
        return f"<Role {self.role_name} ({self.department_name})>"


class UserRole(db.Model):
    __tablename__ = "users_roles"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), primary_key=True)

    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"
