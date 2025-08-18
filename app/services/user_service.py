from datetime import datetime, timezone
from werkzeug.exceptions import NotFound, BadRequest
from ..models import User, UserStatusEnum
from ..extensions import db, bcrypt


def create_user(username, email, password):
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User registered", "username": new_user.username}


def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    return user


def toggle_status(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFound("User not found")

    try:
        # Toggle the user status
        current_status = user.status
        new_status = UserStatusEnum.INACTIVE if current_status == UserStatusEnum.ACTIVE else UserStatusEnum.ACTIVE
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

    if user:
        pass
        # print(f"found user: {user.username}")
        # print(f"email: {email}")
        # print(f"password: {password}")
        # print(f"db password: {user.password}")
    else:
        print("user not found")

    # User password match and the user status is ACTIVE
    if user.password == password and user.status == UserStatusEnum.ACTIVE:
        return True
    else:
        return False
