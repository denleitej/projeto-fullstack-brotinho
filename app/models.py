
from datetime import datetime, timezone, date
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from hashlib import md5

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True) # !!!!!!!
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    role_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('roles.id')) # FIZ ESSA ADIÇÃO e usei essa comando para link as duas classes: flask db migrate -m "Add role_id to User"
    
    # relacionamento - Lista de objetos Plantas do usuario
    plantas: so.WriteOnlyMapped['Plant'] = so.relationship(back_populates='dono')
    
    # relacionamento com Troca 
    trocas: so.WriteOnlyMapped['Troca'] = so.relationship(back_populates='dono')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Plant(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True) # PK
    planta: so.Mapped[str] = so.mapped_column(sa.String(64), index=True) # Nome da planta
    descricao: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128)) # Descrição
    
    # coluna - ID do autor da postagem (chave estrangeira)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    
    # relacionamento - objeto User que é o autor da postagem
    dono: so.Mapped[User] = so.relationship(back_populates='plantas')
    
    # relacionamento - Lista de tarefas de Planta
    tarefas: so.Mapped[List['Tarefa']] = so.relationship(back_populates='plant_ref', cascade='all, delete-orphan', passive_deletes=True)

    
    def __repr__(self):
        return f'<Plant {self.planta}>'


class Tarefa(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True) # PK
    titulo: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)  # Titulo da tarefa
    tipo: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))  # Descrição da tarefa
    data_programada: so.Mapped[date] = so.mapped_column(sa.DateTime) # Data para qual deve ser realizada

    # FK para a planta
    plant_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Plant.id, ondelete="CASCADE"), index=True)
    
    # Relacionamento com Plant
    plant_ref: so.Mapped[Plant] = so.relationship(back_populates='tarefas')

    def __repr__(self):
        return f'<Tarefa {self.titulo}>'

class Troca(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True) # PK
    titulo: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)  # Titulo da troca
    local: so.Mapped[str] = so.mapped_column(sa.String(128))  # Local
    descricao: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))  # Descrição da troca
    
    # Foreign key para User dono do post
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    
    # relacionamento com User
    dono: so.Mapped[User] = so.relationship(back_populates='trocas')
    
    def __repr__(self):
        return f'<Troca {self.titulo}>'
    
    

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
            
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                 role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()
        
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm
    
    def reset_permissions(self):
        self.permissions = 0
    
    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name