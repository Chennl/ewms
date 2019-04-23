from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField,DateTimeField,TextAreaField,HiddenField 
from wtforms.validators import ValidationError, DataRequired, Length
from sqlalchemy import and_,or_
from app.models import Material

class ProjectForm(FlaskForm):
    id=IntegerField('ID')
    wbscode = StringField('工程编号')
    year = IntegerField('工程年份')
    name = StringField('工程名称')
    created_date = DateTimeField('建立日期')
    submit = SubmitField('查 询')
 