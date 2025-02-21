from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
import sqlalchemy as sa
from acl import init_acl

# สร้าง instance ของ SQLAlchemy
bcrypt = Bcrypt()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def init_app(app):
    db.init_app(app)
    bcrypt.init_app(app)
    init_acl(app)
    with app.app_context():
        db.create_all()
        db.reflect()

# โมเดล Role
class Role(db.Model):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False, default="user")
    created_date = mapped_column(sa.DateTime(timezone=True), server_default=func.now())

# โมเดล User
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String)
    status = db.Column(db.String, default="active")
    _password_hash = db.Column(db.String)

    created_date = mapped_column(sa.DateTime(timezone=True), server_default=func.now())
    updated_date = mapped_column(sa.DateTime(timezone=True), server_default=func.now())

    roles: Mapped[list[Role]] = relationship("Role", secondary="user_roles")

    # ✅ เชื่อมกับ Task
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")

    # Password hash management
    @hybrid_property
    def password_hash(self):
        raise Exception("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode("utf-8"))
        self._password_hash = password_hash.decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode("utf-8"))

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

# ตารางกลางสำหรับการเชื่อมโยงผู้ใช้และบทบาท
user_roles = db.Table(
    "user_roles",
    db.Model.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("role_id", sa.ForeignKey("roles.id"), primary_key=True),
)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String)
    data = db.Column(db.LargeBinary)
    created_date = mapped_column(sa.DateTime(timezone=True), server_default=func.now())
    updated_date = mapped_column(sa.DateTime(timezone=True), server_default=func.now())

# ✅ โมเดล Task
class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    due_date: Mapped[sa.DateTime] = mapped_column(sa.DateTime, nullable=True)
    status: Mapped[str] = mapped_column(sa.String, default="Pending")
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    created_date = mapped_column(sa.DateTime(timezone=True), server_default=func.now())
    updated_date = mapped_column(sa.DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now())

    # ✅ เชื่อมโยง Task กับ User
    user: Mapped["User"] = relationship("User", back_populates="tasks")


class UserProfile(db.Model):
    __tablename__ = "user_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    nickname = db.Column(db.String, nullable=True)
    faculty = db.Column(db.String, nullable=True)
    student_id = db.Column(db.String, nullable=True)
    
    user = relationship("User", back_populates="profile")

# เชื่อม `UserProfile` กับ `User`
User.profile = relationship("UserProfile", uselist=False, back_populates="user")
