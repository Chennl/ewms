from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField,DateTimeField,TextAreaField,HiddenField 
from wtforms.validators import ValidationError, DataRequired, Length
from sqlalchemy import and_,or_
from app.models import Material

class MaterialQueryForm(FlaskForm):
    id=IntegerField('ID')
    code = StringField('编号')
    category = StringField('分类')
    name = StringField('名称')
    specification = StringField('规格型号')
    submit = SubmitField('查 询')

class MaterialForm(FlaskForm):
    id=HiddenField ('ID')
    code = StringField('材料编号',validators=[Length(min=1,max=64,message='编号需要1-64个字符')])
    category = StringField('分类',validators=[Length(min=1,max=64,message='分类名称需要2-64个字符')])
    name = StringField('材料名称',validators=[Length(min=1,max=64,message='材料名称需要2-64个字符')])
    specification = StringField('规格型号',validators=[Length(min=1, max=128,message='材料规格型需要2-64个字符')])
    unit = StringField('单位',validators=[Length(min=1, max=16,message='编号需要1-64个字符')])
    remark = TextAreaField('备注',validators=[Length(min=0, max=140,message='备注不能超过140个字符')])
    last_updated = DateTimeField('修改日期')
    updated_by  = StringField('最后修改')
    submit = SubmitField('保存')

    # def validate_code(self,code):
    #     material = Material.query.filter(Material.code==self.code.data).filter(Material.id !=self.id.data).first()
    #     if material is not None:
    #         raise ValidationError('应该材料编号已存在，请使用其它编号！')
    
    # def validate_name(self,name):
    #     material = Material.query.filter(Material.name==self.name.data).filter(Material.id !=self.id.data).first()
    #     if material is not None:
    #         raise ValidationError('应该材料名称已存在，请使用其它名称！')
 