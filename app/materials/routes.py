from flask import render_template,request,current_app,url_for,json,flash,redirect
from flask_login import login_required,current_user
from datetime import datetime
from sqlalchemy import and_
from app.materials import bp
from app.models import Material
from app.materials.forms import MaterialQueryForm,MaterialForm
from app import db
 

# @bp.route('add',methods=['GET','POST'])
# def add():
#     form = MaterialForm()
#     if form.validate_on_submit():
#         material = Material()
#         material.code = form.code.data
#         material.name = form.name.data
#         material.specification = form.specification.data
#         material.unit = form.unit.data  
#         material.remark = form.remark.data
#         material.last_updated = datetime.now()
#         updated_by='chennl'
#         db.session.add(material)
#         db.session.commit()
#         flash('New Material have been saved.')
#         return redirect(url_for('materials.index'))
#     elif request.method=='GET':
#         form.id.data = 0
     
#     return render_template('materials/edit.html',title='添加新材料',form=form)


# @bp.route('edit/<id>',methods=['GET','POST'])
# def edit(id):
#     form = MaterialForm()
#     if form.validate_on_submit():
#         material = Material.query.get(int(id))
#         material.code = form.code.data
#         material.name = form.name.data
#         material.specification = form.specification.data
#         material.unit = form.unit.data  
#         material.remark = form.remark.data
#         material.last_updated = datetime.now()
#         updated_by='chennl'
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('materials.index'))
#     elif request.method=='GET':
#         material = Material.query.get(int(id))
#         form.id.data = material.id
#         form.code.data =material.code
#         form.category.data =material.category
#         form.name.data = material.name
#         form.specification.data = material.specification
#         form.unit.data = material.unit
#         form.remark.data = material.remark
#     return render_template('materials/edit.html',title='材料信息维护',form=form)
        


# @bp.route('/index_amazeui', methods=['GET','POST'])
# def index():
#     form = MaterialQueryForm()
#     method = request.method
#     per_page = current_app.config['MATERIALS_PER_PAGE']
#     page=1
#   #  current_app.logger.info(json.dumps(method))
#     flash(form.validate_on_submit())
#     materials = None
#     if form.validate_on_submit():
#         code = form.code.data.strip()
#         name = form.name.data.strip()
#         specification = form.specification.data.strip()
#         query = db.session.query(Material)
#         if code != "":
#           query = query.filter(Material.code.like('%%%s%%'%code))
#         if name != "":
#           query = query.filter(Material.name.like('%%%s%%'%name))
#         if specification != "":
#           query = query.filter(Material.specification.like('%%%s%%'%specification))

#         materials = query.order_by(Material.name).paginate(1,per_page,False)
#     else:
#         page = request.args.get('page',1,type=int)
#         materials = Material.query.order_by(Material.name).paginate(page,per_page,False)
   
#     next_url = url_for('materials.index',page=materials.next_num) \
#          if materials.has_next else None
#     prev_url = url_for('materials.index',page=materials.prev_num) \
#         if materials.has_prev else None
#     total = materials.total
#     pages = materials.pages
    
#     if page -  4 <= 0:
#       page_start=0
#     else:
#       page_start = page - 4

#     if page +4 > pages:
#       page_end=pages
#     elif pages>8 and page +4<8:
#       page_end =8
#     else:
#       page_end = page +4

#     return render_template('materials/index_amazeui.html', title='材料管理',form =form, \
#     materials =materials.items,next_url=next_url,prev_url=prev_url,total=total,pages=pages,page_start=page_start,page_end=page_end) 
  


 
@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
@login_required
def index():
   return render_template('materials/index.html', title='材料管理') 