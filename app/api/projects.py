from flask import jsonify,request
from datetime import datetime,timedelta,date
from app.models import Project,ProjectMaterial,Material,WarehouseNote,WarehouseNoteItem
from app.api import bp
from app.api.errors import bad_request,error_response
from app import db
from sqlalchemy import and_ 
from sqlalchemy import case

from flask_login import current_user,login_user,logout_user
from app.models import User

# @bp.before_app_request
# def before_request():
#     if not current_user.is_authenticated:
#         user = User.query.get(1)
#         if user is None:
#             user= User(username='chennl',email='chennl@126.com')
#             user.set_password('123456')
#             db.session.add(user)
#             db.session.commit()
#             user = User.query.get(1)
#         login_user(user,remember=True)
    
      

@bp.route('/projects/<int:id>',methods=['GET'])
def get_project(id):
    return jsonify(Project.query.get_or_404(id).to_dict())

@bp.route('/projects',methods=['GET'])
def get_projects():
    page = request.args.get('page',1, type=int)
    per_page = min(request.args.get('per_page',10,type=int),50)

    name = request.args.get('name','')
    #year = request.args.get('year','')
    area = request.args.get('area','')
    category = request.args.get('category','')
    reserve_code = request.args.get('reservecode','')
 

    query =Project.query
    if name is not None and len(name)>0:
        query = query.filter( Project.name.like('%%%s%%'%name))
    if area is not None and len(area)>0:
        query = query.filter( Project.area.like('%%%s%%'%area))
    if category is not None and len(category)>0:
        query = query.filter( Project.category.like('%%%s%%'%category))
    if reserve_code is not None and len(reserve_code)>0:
        query = query.filter( Project.reserve_code.like('%%%s%%'%reserve_code))
    # if year is not None and len(year)>0:
    #     query = query.filter( Project.year.like('%%%s%%'%year))

    data = Project.to_collection_dict(query,page,per_page,'api.get_projects')
    return jsonify(data)


@bp.route('/projects',methods=['POST'])
def create_project():
    data = request.get_json() or {}
    if 'wbscode' not in data or 'name' not in data or 'year' not in  data:
        return bad_request('must include wbscode,name,year fields.')
    # if Project.query.filter_by(wbscode=data['wbscode']).first():
    #     return {'code':61001,'msg':'工程编号已经被占用，请使用不同工程编号'}
    if Project.query.filter_by(name=data['name']).first():
        return {'code':61002,'msg':'工程名称已经被占用，请使用不同工程名称'}
    project =Project()
    project.from_dict(data,new_project=True)
     
    db.session.add(project)
    db.session.commit()
   # db.session.query(func.max(User.tid)).one()[0]
    data = {'code':200,'msg':'工程添加成功'}
    return jsonify(data)

    

@bp.route('/projects/<int:id>',methods=['PUT'])
def update_project(id):
# try:
    project = Project.query.get_or_404(id)
    data = request.get_json() or {}
    project.from_dict(data, new_project=False)
    db.session.commit()

   # project_id = data['project_id']
    if 'items' in data:
        for item in data['items']:
            if item['quantity'] is None or item['quantity']=='':
                item['quantity']='0'
            quantity = float(item['quantity'])  
            material_id  = int(item['material_id']) 

            propejctMaterial = ProjectMaterial.query.filter(and_(ProjectMaterial.project_id==project.id,ProjectMaterial.material_id==material_id)).first()

            if propejctMaterial is not None:
                propejctMaterial.quantity = quantity
                if quantity==0:
                    db.session.delete(propejctMaterial)
                db.session.commit()
            else:
                if quantity>0:
                    propejctMaterial = ProjectMaterial(material_id=material_id,quantity=quantity,project_id=project.id)
                    db.session.add(propejctMaterial)
                    db.session.commit()
    data = {'code':200,'msg':'工程更新成功!'}
# except Exception as e:
#     print(e)
    
    return jsonify(data)

@bp.route('/projects/<int:id>',methods=['DELETE'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    data = {'code':200,'msg':'工程成功!'}
    return jsonify(data)

@bp.route('/projects/<int:id>/materials', methods=['GET'])
def get_project_materials(id):
    project = Project.query.get(id)
    data={}
    if project is None:
        data = {'status':0,  'items': []}
    else:
        data = {
        'status':0,
        'items': [
                {
                'id':item.id,
                'material_id':item.material_id,
                'material_category':item.material.category,
                'material_code':item.material.code,
                'material_name':item.material.name,
                'quantity':item.quantity,
                'material_specification':item.material.specification,
                'category':item.material.category,
                'unit':item.material.unit,
                'remark':item.remark,
                'updated_date':item.updated_date.isoformat(),
                'updated_by':item.updated_by
                } for item in project.materials],
        }
    return jsonify(data)

    
@bp.route('/projects/<int:id>/materirals_back', methods=['GET'])
def get_project_materials_back(id):
  #  id = request.args.get('id',0, type=int)
    page = request.args.get('page',1, type=int)
    per_page = min(request.args.get('per_page',50,type=int),50)
    query = db.session.query(ProjectMaterial.id,
            ProjectMaterial.quantity,
            ProjectMaterial.remark,
            ProjectMaterial.updated_date, 
            ProjectMaterial.updated_by,
            ProjectMaterial.material_id, 
            Material.code.label('material_code'),
            Material.name.label('material_name'),
            Material.unit.label('material_unit'),
            Material.specification.label('material_specification'),
            Material.category).join(Material,Material.id==ProjectMaterial.material_id).filter(ProjectMaterial.project_id==id)
    #print(str(query))
    resources = query.paginate(page, per_page, False)
    data = {
        'status':0,
        'items': [
                    {
                    'id':item.id,
                    'material_id':item.material_id,
                    'material_code':item.material_code,
                    'material_name':item.material_name,
                    'quantity':item.quantity,
                    'material_code':item.material_code,
                    'material_specification':item.material_specification,
                    'category':item.category,
                    'unit':item.material_unit,
                    'remark':item.remark,
                    'updated_date':item.updated_date.isoformat(),
                    'updated_by':item.updated_by
                    } for item in resources.items],
        '_meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': resources.pages,
            'total_items': resources.total
        }
    }

    return jsonify(data)


@bp.route('/projects/<int:projectId>/materials',methods=['POST'])
def add_project_materials(projectId):
    data = request.get_json() or {}
    if 'mids' not in data or 'pid' not in data:
        return bad_request('must include pid,mids fields.')
    if Project.query.filter_by(id=data['pid']).first() is None:
        return {'code':200,"errcode":61001,'msg':'工程不存在'}
    project_id = data['pid']
    print(project_id)
    material_ids = data['mids']
    for mid in material_ids:
        print(mid)
        if ProjectMaterial.query.filter_by(material_id=mid).filter_by(project_id=project_id).first() is None:
            projectMaterial =ProjectMaterial(material_id=mid,quantity=1,project_id=project_id,updated_date=datetime.now(),updated_by='system')
            db.session.add(projectMaterial)
            db.session.commit()
    data = {'code':200,'msg':'工程材料添加成功'}
    return jsonify(data)

@bp.route('/projects/<int:id>/materials',methods=['PUT'])
def update_project_materials(id):
    data = request.get_json() or {}
    if 'quantity' not in data or 'material_id' not in data:
        return bad_request('must include material_id,quantity fields.')
    material = ProjectMaterial.query.filter_by(id=data['id']).filter_by(material_id=data['material_id']).first()
    if material is None:
        return {'code':200,"errcode":61001,'msg':'该工程该材料不存在'}
    material.quantity = data['quantity']
    material.updated_date = datetime.now()
    material.updated_by = current_user.username
    db.session.commit()
    data = {'code':200,'msg':'工程材料更新成功'}
    return jsonify(data)
@bp.route('/projects/<int:projectId>/materials/<int:id>',methods=['DELETE'])
def delete_project_material(projectId,id):
    material = ProjectMaterial.query.get(id)
    if material is not None:
        db.session.delete(material)
        db.session.commit()
    data = {'code':200,'msg':'工程材料删除成功'}
    return jsonify(data)


@bp.route('/projects/<int:id>/warehousenote',methods=['GET'])
def get_project_warehousenotes(id):
    query = WarehouseNote.query.filter_by(project_id=id)
    page = request.args.get('page',1, type=int)
    per_page = min(request.args.get('per_page',10,type=int),50)
    data = WarehouseNote.to_collection_dict(query,page,per_page,'api.get_project_warehousenotes')
    return jsonify(data)

def get_project_warehousenotes(projectId,typeCode,endpoint):
    page = request.args.get('page',1, type=int)
    per_page = min(request.args.get('per_page',10,type=int),50)
    date_range= request.args.get('daterange','')
    to_date=date.today()
    from_date =to_date - timedelta(days=30)
    dates = date_range.split('~')
    if len(dates)==2:
        from_date = dates[0].strip()
        to_date =    dates[1].strip()
    query = WarehouseNote.query.filter(and_(WarehouseNote.project_id==projectId,WarehouseNote.note_type==typeCode,WarehouseNote.note_date.between(from_date,to_date)))
    query.order_by(WarehouseNote.note_date.asc())
    data = WarehouseNote.to_collection_dict(query,page,per_page,endpoint)
    return data
def add_project_warehousenotes(typeCode):
    data = request.get_json() or {}
    if 'warehouse_id' not in data:
        data['warehouse_id']='default'
    if 'project_id' not in data or 'note_date' not in data or 'warehouse_id' not in data or 'note_no' not in data:
        return error_response(40038,'不合法的请求格式')
    data["note_type"]=typeCode   
    note = WarehouseNote()
    data["note_date"]= datetime.strptime(data["note_date"],'%Y-%m-%d')
    note.from_dict(data)
    if 'items' in data:
        for item in data["items"]:
            if item['quantity'] is None:
                continue
            quantity=float(item['quantity'])
            if quantity>0:
                note_item = WarehouseNoteItem(material_id=item['material_id'],quantity=quantity)
                note.items.append(note_item)
    db.session.add(note)
    db.session.commit()
    data = {'code':200,'msg':'%s新增操作成功'%(typeCode)}
    return data
def update_project_warehousenotes(noteId,typeCode):
    data = request.get_json() or {}
    if 'warehouse_id' not in data:
        data['warehouse_id']='default'
    if 'project_id' not in data or 'note_date' not in data or 'warehouse_id' not in data or 'note_no' not in data:
        return error_response(40038,'不合法的请求格式')
    data["note_type"]=typeCode   
    note = WarehouseNote.query.get(noteId)
    note.warehouse_id = data['warehouse_id']
    note.note_no = data['note_no']
    note.note_date = datetime.strptime(data['note_date'],'%Y-%m-%d')
    note.remark = data['remark'] 
    note.updated_date = datetime.utcnow()
    if current_user.is_authenticated:
        note.updated_by = current_user.username
    else:
        note.updated_by = 'anonymous'
    db.session.commit()

    if 'items' in data:
        for item in data['items']:
            if item['quantity'] is None or item['quantity']=='':
                item['quantity']='0'
            quantity = float(item['quantity'])  
            note_item = WarehouseNoteItem.query.filter_by(note_id=noteId).filter_by(material_id=item['material_id']).first()
            if note_item is not None:
                note_item.quantity = quantity
                if quantity==0:
                    db.session.delete(note_item)
                db.session.commit()
            else:
                if quantity>0:
                    note_item = WarehouseNoteItem(material_id=item['material_id'],quantity=quantity,note_id=noteId)
                    db.session.add(note_item)
                    db.session.commit()
    data = {'code':200,'msg':'%s更新操作成功'%(typeCode)}
    return data
def delete_project_warehousenotes(noteId,typeCode):
    note = WarehouseNote.query.get(noteId)
    db.session.delete(note)
    db.session.commit()
    data = {'code':200,'msg':'%s删除操作成功'%(typeCode)}
    return data
#退料单API
@bp.route('/projects/<int:id>/return',methods=['GET'])
def get_warehousenotes_return(id):
    data = get_project_warehousenotes(id,'退料单','api.get_project_return_notes')
    return jsonify(data)
@bp.route('/projects/<int:projectId>/<int:noteId>/warehousereturn',methods=['POST'])
def create_warehousenote_return(projectId,noteId):
    data = add_project_warehousenotes('退料单')
    return jsonify(data)
@bp.route('/projects/<int:projectId>/<int:noteId>/warehousereturn',methods=['PUT'])
def update_warehousenote_return(projectId,noteId):
    data = update_project_warehousenotes(noteId,'退料单')
    return jsonify(data)
@bp.route('/projects/<int:projectId>/<int:noteId>/warehousereturn',methods=['DELETE'])
def delete_warehousenote_return(projectId,noteId):
    data = delete_project_warehousenotes(noteId,'退料单')
    return jsonify(data)

#入库单API
@bp.route('/projects/<int:id>/inbound',methods=['GET'])
def get_project_warehousenotes_inboud(id):
    data = get_project_warehousenotes(id,'入库单','api.get_project_inboud_notes')
    return jsonify(data)
@bp.route('/projects/<int:projectId>/<int:noteId>/warehousing',methods=['POST'])
def create_warehousenote_inload(projectId,noteId):
    data = add_project_warehousenotes('入库单')
    return jsonify(data)
@bp.route('/projects/<int:projectId>/<int:noteId>/warehousing',methods=['PUT'])
def update_warehousenote_inload(projectId,noteId):
    data = update_project_warehousenotes(noteId,'入库单')
    return jsonify(data)
@bp.route('/projects/<int:projectId>/<int:noteId>/warehousing',methods=['DELETE'])
def delete_warehousenote_inload(projectId,noteId):
    data = delete_project_warehousenotes(noteId,'入库单')
    return jsonify(data)

#出库单API
@bp.route('/projects/<int:id>/outbound',methods=['GET'])
def get_project_warehousenotes_outboud(id):
    data = get_project_warehousenotes(id,'出库单','api.get_project_inboud_notes')
    return jsonify(data)

@bp.route('/projects/<int:projectId>/<int:noteId>/warehouseout',methods=['POST'])
def create_warehousenote_outload(projectId,noteId):
    data = add_project_warehousenotes('出库单')
    return jsonify(data)

@bp.route('/projects/<int:projectId>/<int:noteId>/warehouseout',methods=['PUT'])
def update_warehousenote_outload(projectId,noteId):
    data = update_project_warehousenotes(noteId,'出库单')
    return jsonify(data)

@bp.route('/projects/<int:projectId>/<int:noteId>/warehouseout',methods=['DELETE'])
def delete_warehousenote_outload(projectId,noteId):
    data = delete_project_warehousenotes(noteId,'出库单')
    return jsonify(data)

@bp.route('/projects/<int:projectId>/inventory',methods=['GET'])
def get_project_inventory(projectId):
    project_id = projectId
    page = request.args.get('page',1, type=int)
    per_page = 100

    results = db.engine.execute('call sp_inventory_report(%s);'%(project_id))
    rows = results.fetchall()
    
    # # sqlalchemy执行sql
    # data_query = db.session.execute(sql_str)
    # in_sale_query = db.session.execute(in_sale_sql)
    #     # 获取查询到的数据条数
    # total = data_query.rowcount
    # sale_total = in_sale_query.rowcount
    items=[]
    for row in rows:
        project_id,material_id,material_code,category,material_name,specification,material_unit,\
            quantity,inload_total,outload_total,return_total,balance,diff = row
        items.append({
            'project_id':project_id,
            'material_id':material_id,
            'code':material_code,
            'category':category,
            'name':material_name,
            'specification':specification,
            'unit':material_unit,
            'quantity':float(quantity),
            'inload_total':float(inload_total),
            'outload_total':float(outload_total),
            'return_total':float(return_total),
            'balance':float(balance),
            'diff':float(diff)
        })
 
    # data = {
    #     'status':0,
    #     'items': items,
    #     '_meta': {
    #         # 'page': page,
    #         # 'per_page': per_page,
    #         # 'total_pages': resources.pages,
    #         # 'total_items': resources.total
    #     }
#     items.append({
    # #            'project_id':project_id,
    #             'material_id':material_id,
    #             'code':code,
    #             'category':category,
    #             'name':name,
    #             'specification':specification,
    #             'unit':unit,
    #             'quantity':quantity,
    #             'inload_total':outload_total,
    #             'outload_total':outload_total,
    #             'return_total':return_total,
    #             'balance':balance,
    #             'diff':diff
    #         })

    # sbq = db.session.query(WarehouseNote.project_id.label('project_id'),WarehouseNoteItem.material_id.label('material_id'),
    #     db.func.sum(case([
    #         (WarehouseNote.note_type == '入库单',WarehouseNoteItem.quantity.label('inload'))],
    #          else_=0),
    #     ).label('inload_total'),
    #      db.func.sum(case([
    #         (WarehouseNote.note_type == '出库单',WarehouseNoteItem.quantity.label('outload'))],
    #          else_=0),
    #     ).label('outload_total'),
    #      db.func.sum(case([
    #         (WarehouseNote.note_type == '退料单',WarehouseNoteItem.quantity)],
    #          else_=0),
    #     ).label('return_total')).join(WarehouseNoteItem,WarehouseNote.id ==WarehouseNoteItem.note_id)\
    #         .filter(WarehouseNote.project_id==project_id)\
    #         .group_by(WarehouseNote.project_id,WarehouseNoteItem.material_id).subquery()
    
    # sbq_note = db.session.query(
    #         ProjectMaterial.material_id,
    #         ProjectMaterial.quantity,
    #         sbq.c.inload_total,
    #         sbq.c.outload_total,
    #         sbq.c.return_total,
    #     ).outerjoin(sbq,ProjectMaterial.material_id == sbq.c.material_id).filter(ProjectMaterial.project_id==project_id).subquery()

 
    # query = db.session.query(
    #     Material.id.label('id'),
    #     Material.code.label('code'),
    #     Material.category.label('category'),
    #     Material.name.label('name'),
    #     Material.specification.label('specification'),
    #     Material.unit.label('unit'),
    #     sbq_note.c.quantity,
    #     sbq_note.c.inload_total,
    #     sbq_note.c.outload_total,
    #     sbq_note.c.return_total
    # ).join(sbq_note,Material.id == sbq_note.c.material_id).order_by(Material.id.desc())

    # items =[]
    # for item in query.all():
    #    # project_id=item[0],
    #     tpl = tuple(item)
    #     material_id,code,category,name,specification,unit,quantity,inload_total,outload_total,return_total=tpl
    #     i = float(0 if inload_total is None else inload_total)
    #     o= float(0 if outload_total is None else outload_total) + float(0 if return_total is None else return_total)
    #     balance= -1.000*o +i
    #     diff= -1.000*i + float(0 if quantity is None else quantity)  
    #     items.append({
    # #            'project_id':project_id,
    #             'material_id':material_id,
    #             'code':code,
    #             'category':category,
    #             'name':name,
    #             'specification':specification,
    #             'unit':unit,
    #             'quantity':quantity,
    #             'inload_total':outload_total,
    #             'outload_total':outload_total,
    #             'return_total':return_total,
    #             'balance':balance,
    #             'diff':diff
    #         })

    data = {
        'status':0,
        'items': items,
        '_meta': {
            # 'page': page,
            # 'per_page': per_page,
            # 'total_pages': resources.pages,
            # 'total_items': resources.total
        }
    }

 
    return jsonify(data)

 
