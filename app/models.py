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
    password = db.Column(db.String(500), nullable=False)
    status = db.Column(
        db.Enum(UserStatusEnum), nullable=False, default=UserStatusEnum.INACTIVE
    )
    inactive_date = db.Column(db.DateTime, nullable=True)
    public_id = db.Column(db.String(50), unique=True)

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

        # Serialize the related profile (if any) without causing recursion
        p = getattr(self, "profile", None)
        if p is not None:
            data["profile"] = {
                "id": p.id,
                "user_id": p.user_id,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "bio": p.bio,
                "created_at": (
                    p.created_at.isoformat()
                    if hasattr(p.created_at, "isoformat")
                    else p.created_at
                ),
                "updated_at": (
                    p.updated_at.isoformat()
                    if hasattr(p.updated_at, "isoformat")
                    else p.updated_at
                ),
            }
        else:
            data["profile"] = None

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

    def to_dict(self):
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "department_name": self.department_name,
        }

    def __repr__(self):
        return f"<Role {self.role_name} ({self.department_name})>"


class UserRole(db.Model):
    __tablename__ = "users_roles"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), primary_key=True)

    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True
    )
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    bio = db.Column(db.String(500), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )

    # One-to-one relationship: a user has at most one profile
    user = db.relationship("User", backref=db.backref("profile", uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "bio": self.bio,
            "user": {**self.user.to_dict()},
        }

    def __repr__(self):
        return f"<Profile user_id={self.user_id} first_name={self.first_name} last_name={self.last_name}>"
