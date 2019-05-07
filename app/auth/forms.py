from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField,SelectField,FileField,DateTimeField,TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from app.models import Permission

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField('登 录')

class UserProfileForm(FlaskForm):
    id=IntegerField(u'用户ID')
    username = StringField(u'用户名', validators=[DataRequired()])
    nickname = StringField(u'昵称', validators=[DataRequired()])
    email = StringField(u'邮箱', validators=[DataRequired()])
    about_me  = TextAreaField(u'备注')
    last_seen=DateTimeField(u'最近访问时间')

    sex = StringField(u'性别')
    avatar = FileField(u'头像')
    #avatar        = FileField(u'头像', [validators.regexp(u'^[^/\\]\.jpg$')])
    #permission
    p_project_setting=IntegerField(u'工程管理')
    p_warehouse_in=IntegerField(u'入库')
    p_warehouse_out=IntegerField(u'出库')
    p_warehouse_return=IntegerField(u'退库')
    p_material_setting=IntegerField(u'材料')
    p_user_setting=IntegerField(u'用户管理')

    def get_permission(self):
        permissions =0
        if  self.p_project_setting.data is not None:
            permissions += Permission.PROJECT_MGR
        if  self.p_warehouse_in.data is not None:
            permissions += Permission.WAREHOUSE_IN
        if  self.p_warehouse_out.data is not None:
            permissions += Permission.WAREHOUSE_OUT
        if  self.p_warehouse_return.data is not None:
            permissions += Permission.WAREHOUSE_RETURN
        if  self.p_material_setting.data is not None:
            permissions += Permission.MATERIAL_MGR
        if  self.p_user_setting.data is not None:
            permissions += Permission.USER_MGR
        return permissions

    def set_permission(self,permissions):

        if  permissions&Permission.PROJECT_MGR >0:
            self.p_project_setting.data = 1
        if  permissions&Permission.WAREHOUSE_IN >0:
            self.p_warehouse_in.data = 1
        if  permissions&Permission.WAREHOUSE_OUT >0:
            self.p_warehouse_out.data = 1
        if  permissions&Permission.WAREHOUSE_RETURN >0:
            self.p_warehouse_return.data = 1
        if  permissions&Permission.MATERIAL_MGR >0:
            self.p_material_setting.data = 1
        if  permissions&Permission.USER_MGR >0:
            self.p_user_setting.data = 1

 

    submit = SubmitField('立即提交')

 
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password1 = PasswordField( 'New Password', validators=[DataRequired()])
    password2 = PasswordField( 'Repeat Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Request Password Reset')
 