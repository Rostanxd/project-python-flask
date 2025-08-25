from ..models import Role
from ..extensions import db


def create(role_name, department_name):
    new_role = Role(role_name=role_name, department_name=department_name)
    db.session.add(new_role)
    db.session.commit()
    return new_role
