from app.api import bp
from flask import jsonify,request,url_for
from app.models import User
from app.api.errors import bad_request
from app import db
from app.api.auth import token_auth


def to_layui_standard_json(code=0,msg='',items=[],total=0):
    data = {
        'code':code,
        'msg':msg,
        'count':total,
        'data': [item.to_dict() for item in items],
        }
    return data

@bp.route('/users/test',methods=['GET'])
def test():
    return jsonify(to_layui_standard_json())

@bp.route('/users/<int:id>',methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/users', methods=['GET'])
#@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('limit', 10, type=int), 100)
    query = User.query.filter(User.username != 'Chennl')
    data = User.to_collection_dict(query, page, per_page, 'api.get_users')
    
    resources = query.paginate(page, per_page, False)
    data = to_layui_standard_json(0,'',resources.items,resources.total)

    return jsonify(data)

@bp.route('/users/<int:id>/followers', methods=['GET'])
def get_followers(id):
    pass

@bp.route('/users/<int:id>/followed', methods=['GET'])
def get_followed(id):
    pass

@bp.route('/users', methods=['POST'])
#@token_auth.login_required
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/users/<int:id>', methods=['PUT'])
#@token_auth.login_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())