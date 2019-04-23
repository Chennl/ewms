from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField,SelectField,FileField,DateTimeField,TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo

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
    submit = SubmitField('立即提交')

 
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password1 = PasswordField( 'New Password', validators=[DataRequired()])
    password2 = PasswordField( 'Repeat Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Request Password Reset')
 