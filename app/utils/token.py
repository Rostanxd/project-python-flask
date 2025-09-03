from flask import request, jsonify, current_app
from functools import wraps

import jwt

from ..models import User


def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")

        if not authorization:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            token = authorization.split(" ")[1]  # Exclude "Bearer" word
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = User.query.filter_by(public_id=data["public_id"]).first()
        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated
