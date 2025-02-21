from wtforms_sqlalchemy.orm import model_form
from flask_wtf import FlaskForm
from wtforms import Field, widgets, validators, fields
import models
from flask_wtf import FlaskForm, file



# ฟอร์มการลงทะเบียนและเข้าสู่ระบบ
BaseUserForm = model_form(
    models.User,
    base_class=FlaskForm,
    exclude=["created_date", "updated_date", "status", "_password_hash"],
    db_session=models.db.session,
)


class LoginForm(FlaskForm):
    username = fields.StringField("Username", [validators.DataRequired()])
    password = fields.PasswordField("Password", [validators.DataRequired()])


class RegisterForm(BaseUserForm):
    username = fields.StringField(
        "Username", [validators.DataRequired(), validators.Length(min=6)]
    )
    password = fields.PasswordField(
        "Password", [validators.DataRequired(), validators.Length(min=6)]
    )
    name = fields.StringField(
        "Name", [validators.DataRequired(), validators.Length(min=6)]
    )

class TaskForm(FlaskForm):
    title = fields.StringField("Task Title", validators=[validators.DataRequired()])
    description = fields.TextAreaField("Task Description")
    due_date = fields.DateTimeField("Due Date", format='%Y-%m-%d %H:%M:%S')  # ✅ เปลี่ยนเป็น DateTimeField
    submit = fields.SubmitField("Save")




BaseUploadForm = model_form(
    models.Upload,
    base_class=FlaskForm,
    db_session=models.db.session,
    exclude=["created_date", "updated_date", "status", "filename"],
)


class UploadForm(BaseUploadForm):
    file = fields.FileField(
        "Upload team image (png or jpg) , Recommended image size:250(px) x 230(px)",
        validators=[
            file.FileAllowed(["png", "jpg", "jpeg"], "You can use onlyjpg , png"),
        ],
    )