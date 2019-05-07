from flask import render_template,request,current_app,url_for,json,flash,redirect
from datetime import datetime
from flask_login import current_user,login_required
from app import db
from app.main import bp
from app.models import Project,User
from app.decorators import admin_required
from app.main.forms import ProjectForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen= datetime.now()
        db.session.commit()
        

@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
        return render_template('main/index.html', title='Sign In')


@bp.route('/admin',methods=['GET'])
@admin_required
def for_admins_only():
    return "For administrators!"

@bp.route('/v/index',methods=['GET'])
def v_index():
    return render_template('vue/index.html') 
 