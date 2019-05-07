import os, base64,datetime
from hashlib import md5 
from flask import redirect,url_for,render_template,flash,request,jsonify,current_app,make_response
from flask_login import current_user,login_user,logout_user,login_required
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from app.models import User
from app.auth import bp
from app.auth.forms import LoginForm,UserProfileForm,ResetPasswordForm
from app import db

from app.api.errors import bad_request,error_response

   
@bp.route('/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误，请重试！')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

    
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
 
        response = current_app.make_response(redirect(next_page) )
        expires_in=datetime.datetime.today() + datetime.timedelta(days=7)
        token = user.get_token()
        db.session.commit()
        response.set_cookie('Name',value='test',expires=expires_in)
        response.set_cookie('token',value=token,expires=expires_in)
        return response
 
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(): 
    form = UserProfileForm()
    if request.method == 'GET':
        if current_user.is_authenticated:
            form.username=current_user.username
            form.nickname=current_user.nickname
            form.email=current_user.email
            form.about_me=current_user.about_me
            form.last_seen=current_user.last_seen
            form.sex=''
            form.avatar=''
        return render_template('auth/editprofile.html',title='',form=form)
    elif form.validate_on_submit:
        current_user.nickname = form.nickname.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        path=os.path.join(os.path.join(os.getcwd(), "app\\static\\avatars", current_user.avatar(100)))
        current_app.logger.info('upload file path is: %s' % path)
       # filepath = get_avatar_filepath('jpg')
        upload_file(path)
        flash('Your changes have been saved.')
        return redirect(url_for('auth.edit_profile'))

@bp.route('/reset_password', methods=['GET', 'POST'])
@login_required 
def reset_password():
     form = ResetPasswordForm()
     if request.method=='POST':
        if form.validate_on_submit():
            if current_user.check_password(form.password.data):
                if form.password1.data == form.password2.data:
                    current_user.set_password(form.password1.data)
                    db.session.commit()
                    flash('密码重置成功')
                    return render_template('auth/resetpassword_success.html', title='Reset Password')
                else:
                    flash('再次密码输入不一致')
            else:
                flash('当前密码不正确')
        else:
            flash('再次密码输入不一致')

     return render_template('auth/resetpassword.html', title='Reset Password',form=form)
    

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set(['png', 'jpg', 'jpeg', 'gif'])


@bp.route('/profile/avatar', methods=['GET', 'POST'])
@login_required
def upload_avater(): 
    data={}
    if request.method == 'POST':
        digest = md5(current_user.username.lower().encode('utf-8')).hexdigest()
        filename=digest+'.jpg'
        path=os.path.join(os.path.join(os.getcwd(), "app\\static\\avatars", filename))
        return upload_file(path)

def upload_file(filepath):
     # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            data =  {'code':200,'msg':'没有文件上传'}
            return jsonify(data)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            data =  {'code':200,'msg':'没有选择上传文件'}
            return jsonify(data)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(filepath)
            data =  {'code':200,'msg':'上传成功'}
        return jsonify(data)
    
@bp.route('/user', methods=['GET', 'POST'])
@login_required
def get_users():
    role = current_user.can_user()
    users = User.query.filter(User.username !='chennl')
    return render_template('auth/user.html',users=users,title='',role=role)

@bp.route('/logout')
def logout(): 
    logout_user()
    return redirect(url_for('auth.login')) 


@bp.route('/user/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit_user(id):
    form = UserProfileForm()
    data={}
    if request.method =='GET':
        user = User.query.get(id)
        form = UserProfileForm(id=user.id,username=user.username,nickname=user.nickname,email=user.email,about_me=user.about_me)
        form.set_permission(user.permission)
        return render_template('auth/useredit.html',title='',form=form,postbackurl='/auth/user/edit/{}'.format(id) ,is_new=False)
    else:
        if form.validate_on_submit():
            user = User.query.get(form.id.data)
            user.nickname=form.nickname.data
            user.email = form.email.data
            user.about_me= form.about_me.data
            user.permission = form.get_permission()
            db.session.commit()
            data={'code':200,'message':'用户更新成功!'}
            #flash('用户更新成功!')
            return success_page("用户信息更新成功!")
        else:
            return render_template('auth/useredit.html',title='',form=form,is_new=False)
            # raise ValidationError('Please use a different username.')


def success_page(msg):
    return render_template('auth/success_page.html',msg=msg)

@bp.route('/user/add',methods=['GET','POST'])
@login_required
def add_user():
    form = UserProfileForm()
    if request.method =='GET':
        form = UserProfileForm(id=0,username='',nickname='',email='',about_me='')
        return render_template('auth/useredit.html',title='',form=form,is_new=True)
    else:
       
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash('用户名已经被使用，请用另外用户名!')
                return  render_template('auth/useredit.html',title='',form=form,postbackurl=url_for('auth.add_user'),is_new=True)
            user = User()
            user.username=form.username.data
            user.nickname=form.nickname.data
            user.email = form.email.data
            user.set_password('123456')
            user.about_me= form.about_me.data
            db.session.add(user)
            db.session.commit()
            #flash('用户添加成功!')
            data={'code':200,'message':'用户添加成功!'}
            #flash('用户更新成功!')
            return success_page("用户信息更新成功!")
            
        else:
             return render_template('auth/useredit.html',title='',form=form,postbackurl=url_for('auth.add_user'),is_new=True)


@bp.route('/user/del/<int:id>',methods=['GET','POST'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    if user.username=='chennl' or user.username=='fangjj' or user.username=='fangdy':
        data={'code':'200','message':'该用户不允许删除'}
        return jsonify(data)
    db.session.delete(user)
    db.session.commit()
    data={'code':'200','message':'用户删除成功'}
    return jsonify(data)

@bp.route('/user/repassword/<int:id>',methods=['POST'])
@login_required
def admin_reset_password(id):
    user = User.query.get(id)
    user.set_password('123456')
    db.session.commit()
    msg={'errcode':'200','errmsg':'用户密码重置成功'}
    # msg={'errcode':'201','errmsg':'用户密码重置失败'}
    return jsonify(msg)