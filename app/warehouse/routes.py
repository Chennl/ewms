from flask import render_template,request,current_app,url_for,json,flash,redirect
 
from app.warehouse import bp
from app.models import Project,ProjectMaterial,Material
 
       

@bp.route('/index', methods=['GET','POST'])
def index():
  projects = Project.query.all()
  return render_template('warehouse/index.html', projects = projects,title='仓库管理') 
 