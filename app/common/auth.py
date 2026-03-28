import jwt
from dataclasses import dataclass
from functools import wraps
from flask import request, g, current_app
from .error_handler import UnauthorizedError


@dataclass
class TokenPayload:
    sub: str
    email: str | None = None


def decode_access_token(token: str) -> TokenPayload:
    secret = current_app.config['JWT_SECRET']
    if not secret:
        raise UnauthorizedError("Server is not configured for authentication")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedError("Token missing sub claim")

    return TokenPayload(sub=sub, email=payload.get("email"))


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise UnauthorizedError("Missing or invalid Authorization header")

        token = auth_header[len("Bearer "):]
        g.user = decode_access_token(token)
        return f(*args, **kwargs)
    return decorated
