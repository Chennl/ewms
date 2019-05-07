import base64,os,json
from hashlib import md5
from datetime import time,datetime,timedelta
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
#import jwt
from flask import url_for,current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,current_user,AnonymousUserMixin,login_manager
from datetime import datetime,date
from app import db,login


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'status':0,
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                # 'self': url_for(endpoint, page=page, per_page=per_page,
                #                 **kwargs),
                # 'next': url_for(endpoint, page=page + 1, per_page=per_page,
                #                 **kwargs) if resources.has_next else None,
                # 'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                #                 **kwargs) if resources.has_prev else None
            }
        }
        return data



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  
    def __repr__(self):
        return '<Post {}>'.format(self.body)

class User(UserMixin,PaginatedAPIMixin,db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140),default='')
    nickname = db.Column(db.String(64),default='')
    last_seen=db.Column(db.DateTime,default=datetime.now)
    token = db.Column(db.String(128))
    token_expiration = db.Column(db.DateTime)
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'),nullable=False,  default=1)
    permission = db.Column(db.Integer ,default=0)
    #role = relationship('Role', backref='users', foreign_keys=[role_id])

    # def __init__(self, **kwargs):
    #     super(self, **kwargs).__init__(**kwargs)
    #     if self.role is None:
    #         self.role = Role.query.filter_by(default = True).first()

    def __repr__(self):
        return '<User {}>'.format(self.username)    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self,expires_in=3600):
        now = datetime.now()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.urlsafe_b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = datetime.now() + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token


    def revoke_token(self):
        self.token_expiration = datetime.now() - timedelta(seconds=1)

    #基于令牌的验证请求方案 -- 开始
    def generate_auth_token(self,expiration = 600):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        self.token = s.dumps({'id':self.id})
        self.token_expiration = datetime.now() + timedelta(seconds=expiration)
        return self.token

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
           data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        return user

    #基于令牌的验证请求方案 --结束
    def avatar(self,size):
        digest = md5(current_user.username.lower().encode('utf-8')).hexdigest()
        filename=digest+'.jpg'
        return filename

    def to_dict(self,include_email=False):
        data ={
            'id':self.id,
            'username':self.username,
            'nickname':self.nickname,
            'about_me':self.about_me,
            'email':self.email,
            'last_seen':self.last_seen.isoformat() 
        }
        if include_email:
            data['email']=self.email
        return data
    def from_dict(self,data,new_user=False):
        for field in ['username','nickname','email','about_me']:
            if field in data:
                setattr(self,field,data[field])
        if new_user:
            if 'password' in data:
                self.set_password(data['password'])

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.now():
            return None
        return user

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions
   
    def is_administrator(self):
        return self.can(Permission.ADMINISTER) 
        
    def can_project(self):
        return (self.permission & Permission.PROJECT_MGR) >0
    def can_warehouse_in(self):
        return (self.permission & Permission.WAREHOUSE_IN)>0
    def can_warehouse_out(self):
        return (self.permission & Permission.WAREHOUSE_OUT)>0
    def can_warehouse_return(self):
        return (self.permission & Permission.WAREHOUSE_RETURN)>0
    def can_user(self):
        return (self.permission & Permission.USER_MGR)>0
    def can_material(self):
        return (self.permission & Permission.MATERIAL_MGR)>0
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Material(PaginatedAPIMixin,db.Model):
    __tablename__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    category = db.Column(db.String(64))
    specification = db.Column(db.String(128))
    unit = db.Column(db.String(16))
    remark = db.Column(db.String(128))
    updated_date = db.Column(db.DateTime,default=datetime.utcnow)
    updated_by  = db.Column(db.String(64))

    def to_dict(self):
        data ={
            'id':self.id,
            'code':self.code,
            'name':self.name,
            'category':self.category,
            'specification':self.specification,
            'unit':self.unit,
            'remark':self.remark,
            'updated_date':self.updated_date
        }
        return data
    def from_dict(self, data, new_material=False):
        for field in ['code', 'name', 'specification','unit','category','remark']:
            if field in data:
                setattr(self, field, data[field])
        setattr(self,'updated_date',datetime.now())
        if new_material:
             pass

class Project(PaginatedAPIMixin,db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    wbscode = db.Column(db.String(64))
    name = db.Column(db.String(128))
    year = db.Column(db.String(64))
    category = db.Column(db.String(128))
    area = db.Column(db.String(128))
    reserve_code = db.Column(db.String(128))
    remark = db.Column(db.String(128))
    created_date = db.Column(db.DateTime,default=datetime.utcnow)
    updated_date = db.Column(db.DateTime,default=datetime.utcnow)
    updated_by  = db.Column(db.String(64))
    #这个不是影响表结构的
    materials = db.relationship('ProjectMaterial',backref='project',lazy='dynamic')
    
    def to_dict(self,include_materials=False):
        data ={
            'id':self.id,
            'wbscode':self.wbscode,
            'name':self.name,
            'year':self.year,
            'reserve_code':self.reserve_code,
            'category':self.category,
            'area':self.area,
            'remark':self.remark,
            'created_date':self.created_date.isoformat(),
            'updated_date':self.updated_date.isoformat(),
            'updated_by':self.updated_by
        }
     
        if include_materials:
            data['materials']=''
        return data

    def set_created_date(self):
        setattr(self,'created_date',datetime.now())

        
    def from_dict(self,data,new_project=False):
        for field in['wbscode','name','year','reserve_code','category','area','remark']:
            if field in data:
                setattr(self,field,data[field])
            setattr(self,'updated_date',datetime.now())
            if current_user.is_authenticated:
                setattr(self,'updated_by',current_user.username)
            else:
                setattr(self,'updated_by','anonymous')
            if new_project:
                self.set_created_date()

    def __repr__(self):
        return '<Project {}>'.format(self.name)

class ProjectMaterial(PaginatedAPIMixin,db.Model):
    __tablename__ = 'project_material'
    id = db.Column(db.Integer, primary_key=True)
    material_id =  db.Column(db.Integer, db.ForeignKey('material.id'))
    material = db.relationship("Material")
    quantity = db.Column(db.String(64))
    remark = db.Column(db.String(128))
    updated_date = db.Column(db.DateTime,default=datetime.utcnow)
    updated_by  = db.Column(db.String(64))
    project_id =  db.Column(db.Integer, db.ForeignKey('project.id'))

 
    def to_dict(self):
        data ={
            'id':self.id,
            'material_id':self.material_id,
            'quantity':self.quantity,
            'remark':self.remark,
            'updated_date':self.updated_date.isoformat(),
            'updated_by':self.updated_by
        }
        return data

    def from_dict(self,data,new_project=False):
        for field in['material_id','quantity','remark']:
            if field in data:
                setattr(self,field,data[field])
            setattr(self,'updated_date',datetime.now())
            if current_user.is_authenticated:
                setattr(self,'updated_by',current_user.username)
            else:
                setattr(self,'updated_by','anonymous')

    def __repr__(self):
        return '<ProjectMaterial {}>'.format(self.quantity)


    
class WarehouseNote(PaginatedAPIMixin,db.Model):
    __tablename__ = 'warehousenote'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.String(16))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project')
    note_no = db.Column(db.String(16))
    note_type = db.Column(db.String(16))    #入库单 出库单 退料单
    note_date = db.Column(db.Date,default=datetime.utcnow) 
    remark = db.Column(db.String(128))
    items = db.relationship('WarehouseNoteItem',backref='warehousenote',lazy='dynamic')
    updated_date = db.Column(db.DateTime,default=datetime.utcnow)
    updated_by  = db.Column(db.String(64))


    def to_dict(self,):
        data={
            'id':self.id,
            'warehouse_id':self.warehouse_id,
            'project_id':self.project_id,
            'note_no':self.note_no,
            'note_date':self.note_date.strftime('%Y-%m-%d'),
            'note_type':self.note_type,
            'updated_by':self.updated_by,
            'remark':self.remark,
        }
        return data

    def from_dict(self,data,is_new=False):
        for field in['project_id','warehouse_id','note_date','note_type','note_no','remark']:
            if field in data:
                setattr(self,field,data[field])
        setattr(self,'updated_date',datetime.now())
        if current_user.is_authenticated:
            setattr(self,'updated_by',current_user.username)
        else:
            setattr(self,'updated_by','anonymous')
    

class WarehouseNoteItem(db.Model):
    __tablename__ = 'warehousenoteitem'
    id = db.Column(db.Integer, primary_key=True)
    note_id =  db.Column(db.Integer, db.ForeignKey('warehousenote.id'))
    material_id =  db.Column(db.Integer, db.ForeignKey('material.id'))
    material = db.relationship("Material")
    quantity = db.Column(db.Float,default=0)
    remark = db.Column(db.String(128))

    def from_dict(self,data):
        for field in['material_id','quantity']:
            if field in data:
                setattr(self,field,data[field])

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64), unique=True)
    is_default = db.Column(db.Boolean,  default = False, index =True) #该角色是否默认角色
    permissions = db.Column(db.Integer) #角色的权限
    #users = db.relationship('User', backref = 'role', lazy = 'dynamic')

class Permission:
    PROJECT_MGR =   0b000000000001 #工程      0b000000000001
    MATERIAL_MGR =  0b000000000010 #材料员    0b000000000010
    WAREHOUSE_IN =      0b000000000100 #仓库员   
    WAREHOUSE_OUT =     0b000000001000 #仓库员   
    WAREHOUSE_RETURN =  0b000000010000 #仓库员   
    USER_MGR =          0b000100000000 #用户管理员 
    ADMINISTER =        0b1000000000000 #超级管理员

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

 