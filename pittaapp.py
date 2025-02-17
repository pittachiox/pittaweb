import os
import flask
import models
import forms
from flask_login import login_required, login_user, logout_user, LoginManager, current_user
from flask import render_template, redirect, url_for, Response, flash, request, abort
from models import db, User, Upload, Task, Role
from werkzeug.utils import secure_filename
from forms import TaskForm


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
models.init_app(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

@app.route("/")
def index():
    tasks = Task.query.order_by(Task.due_date).all()
    return render_template("index.html", tasks=tasks)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.authenticate(form.password.data):
            login_user(user)
            return redirect(url_for("introduce"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists", "danger")
        else:
            user = User()
            form.populate_obj(user)
            role = Role.query.filter_by(name="user").first() or Role(name="user")
            user.roles.append(role)
            user.password_hash = form.password.data
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("index"))
    return render_template("register.html", form=form)

@app.route("/introduce")
@login_required
def introduce():
    return render_template("introduce.html")

@app.route('/detail', methods=['GET', 'POST'])
@login_required
def detail():
    return render_template('detail.html', user=current_user)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    current_user.name = request.form.get('name')
    current_user.nickname = request.form.get('nickname')
    current_user.faculty = request.form.get('faculty')
    current_user.student_id = request.form.get('student_id')
    db.session.commit()

    # โหลดข้อมูลใหม่จากฐานข้อมูล
    db.session.refresh(current_user)

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('images'))


@app.route("/tasks/create", methods=["GET", "POST"])
@login_required
def create_task():
    form = TaskForm()  # ใช้ TaskForm() แทน forms.TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            status="Pending",
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("create_task.html", form=form)

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = forms.UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        file.seek(0)  # รีเซ็ต pointer ของไฟล์ก่อนอ่านข้อมูล
        uploaded_file = Upload(filename=filename, data=file.read())
        db.session.add(uploaded_file)
        db.session.commit()
        
        flash("File uploaded successfully!", "success")  # แจ้งเตือนเมื่ออัปโหลดสำเร็จ
        return redirect(url_for("images"))
    return render_template("upload.html", form=form)

@app.route("/images")
@login_required
def images():
    user = User.query.get(current_user.id)  # โหลดข้อมูลใหม่จากฐานข้อมูล
    return render_template("images.html", user=user)



@app.route("/upload/<int:file_id>")
@login_required
def get_uploaded_image(file_id):
    file_ = Upload.query.get_or_404(file_id)
    return Response(file_.data, headers={"Content-Disposition": f'inline;filename="{file_.filename}"', "Content-Type": "application/octet-stream"})

if __name__ == "__main__":
    app.run(debug=True)


