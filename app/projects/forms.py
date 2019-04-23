from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField,DateTimeField,TextAreaField,HiddenField 
from wtforms.validators import ValidationError, DataRequired, Length
from sqlalchemy import and_,or_
from app.models import Project
 

class ProjectForm(FlaskForm):
    id=HiddenField ('ID')
    wbscode = StringField('工程编号',validators=[Length(min=1,max=64,message='编号需要1-64个字符')])
    name = StringField('工程名称',validators=[Length(min=1,max=64,message='名称需要2-64个字符')])
    year = StringField('工程年份',validators=[Length(min=1, max=128,message='工程需要4位数字')])
    remark = TextAreaField('备注',validators=[Length(min=0, max=140,message='备注不能超过140个字符')])
    created_date = DateTimeField('创建日期')
    updated_date  = StringField('修改日期')
    updated_by  = StringField('修改人员')
    submit = SubmitField('保存')
 
 