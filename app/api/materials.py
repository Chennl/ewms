from flask import jsonify,request
from sqlalchemy import or_,func
from app.api import bp
from app.models import Material
from app.api.errors import bad_request
from app import db

@bp.route('/materials/<int:id>',methods=['GET'])
def get_material(id):
    return jsonify(Material.query.get_or_404(id).to_dict())

@bp.route('/materials',methods=['GET'])
def get_materials():
    page = request.args.get('page',1, type=int)
    per_page = min(request.args.get('per_page',10,type=int),50)
   
    name = request.args.get('name','')
    specification = request.args.get('specification','')
    category = request.args.get('category','')
    code = request.args.get('code','')
 
    query =Material.query
    if name is not None and len(name.strip())>0:
        query = query.filter( Material.name.like('%%%s%%'%name))
    if category is not None and len(category.strip())>0:
        query = query.filter( Material.category.like('%%%s%%'%category))
    if code is not None and len(code.strip())>0:
        query = query.filter( Material.code.like('%%%s%%'%code))
    if specification is not None and len(specification.strip())>0:
        query = query.filter( Material.specification.like('%%%s%%'%specification))


        #query = query.filter(or_(Material.name.like('%%%s%%'%keyword),Material.specification.like('%%%s%%'%keyword)))
   # print(str(query))
    data = Material.to_collection_dict(query,page,per_page,'api.get_materials')


    return jsonify(data)

@bp.route('/materials',methods=['POST'])
def create_material():
    data = request.get_json() or {}
    if 'code' not in data or 'name' not in data or 'specification' not in data:
        return bad_request('must inlcude code,name,specification fields.')
    if 'code' in data and  Material.query.filter_by(code=data['code']).first():
        return bad_request('please use a different code.')
    # if 'name' in data and Material.query.filter_by(name=data['name']).first():
    #     return bad_request('plase use a different name.')

    material = Material()
    material.from_dict(data,new_material=True)
    db.session.add(material)
    db.session.commit()
    response = jsonify(material.to_dict())
    response.status_code = 201
    data = {'code':200,'msg':'添加成功!'}
    return jsonify(data)

@bp.route('/materials/<int:id>',methods=['PUT'])
def save_material(id):
    material = Material.query.get_or_404(id)
    data = request.get_json() or {}
    # if 'code' in data and data['code'] != material.code and \
    #         Material.query.filter_by(code=data['code']).first():
    #     return bad_request('please use a different code.')
    # if 'name' in data and data['name'] != material.name and \
    #         Material.query.filter_by(name=data['name']).first():
    #     return bad_request('plase use a different name.')

    material.from_dict(data, new_material=False)
    db.session.commit()
 #   return jsonify(material.to_dict())
    data = {'code':200,'msg':'保存成功!','data':data}
    return jsonify(data)

@bp.route('/materials/<int:id>',methods=['DELETE'])
def delete_material(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    data = {'code':200,'msg':'删除成功!'}
    return jsonify(data)