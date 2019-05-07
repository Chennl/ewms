from flask import g,current_app
from flask_httpauth import HTTPBasicAuth,HTTPTokenAuth
from app.api.errors import error_response
from app.models import User

basic_auth = HTTPBasicAuth()

token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username_or_token,password):
    #first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if user is None:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.check_password(password):
            return False
    g.current_user = user
    return True


@basic_auth.error_handler
def basic_auth_error():
    return error_response(401)

@token_auth.verify_token
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    
    return g.current_user is not None

@token_auth.error_handler
def token_auth_error():
    return error_response(401)


