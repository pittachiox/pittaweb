import flask
import models
import forms
from flask_login import login_required, login_user, logout_user, LoginManager, current_user
from flask import render_template, redirect, url_for, Response, send_file, abort, flash, request
from models import db, User

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
models.init_app(app)


@app.route("/")
def index():
    db = models.db
    tasks = db.session.execute(
        db.select(models.Task).order_by(models.Task.due_date)
    ).scalars()
    return flask.render_template("index.html", tasks=tasks)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        if user and user.authenticate(form.password.data):
            login_user(user)
            return redirect(url_for("introduce"))  # เปลี่ยนจาก index เป็น introduce
        return render_template("login.html", form=form, error="Invalid username or password")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if not form.validate_on_submit():
        return render_template("register.html", form=form)

    # ตรวจสอบว่า username มีอยู่แล้วหรือไม่
    existing_user = models.User.query.filter_by(username=form.username.data).first()
    if existing_user:
        return render_template("register.html", form=form, error="Username นี้มีอยู่แล้ว กรุณาใช้ชื่ออื่น")

    user = models.User()
    form.populate_obj(user)

    # ตรวจสอบ role user
    role = models.Role.query.filter_by(name="user").first()
    if not role:
        role = models.Role(name="user")
        models.db.session.add(role)

    user.roles.append(role)
    user.password_hash = form.password.data
    models.db.session.add(user)

    try:
        models.db.session.commit()
    except Exception as e:
        models.db.session.rollback()
        return render_template("register.html", form=form, error="เกิดข้อผิดพลาดในการลงทะเบียน กรุณาลองใหม่อีกครั้ง")

    # ล็อกอินอัตโนมัติ
    login_user(user)

    return redirect(url_for("login"))  # หลังล็อกอินให้ไปหน้า Index 

@app.route("/introduce")
@login_required
def introduce():
    return flask.render_template("introduce.html")

@app.route('/detail', methods=['GET', 'POST'])
@login_required
def detail():
    return render_template('detail.html')

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # รับค่าจากฟอร์ม
        current_user.name = request.form.get('name')
        current_user.nickname = request.form.get('nickname')
        current_user.faculty = request.form.get('faculty')
        current_user.student_id = request.form.get('student_id')

        # บันทึกลงฐานข้อมูล
        db.session.commit()
        flash('ข้อมูลถูกอัปเดตเรียบร้อย!', 'success')

    return redirect(url_for('detail'))

@app.route("/tasks/create", methods=["GET", "POST"])
@login_required
def create_task():
    form = forms.TaskForm()
    if form.validate_on_submit():
        task = models.Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            status="Pending",
            user_id=current_user.id,
        )
        db = models.db
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("create_task.html", form=form)


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def update_task(task_id):
    db = models.db
    task = models.Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    form = forms.TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("update_task.html", form=form, task=task)


@app.route("/tasks/<int:task_id>/complete")
@login_required
def mark_complete(task_id):
    db = models.db
    task = models.Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    task.status = "Completed"
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    db = models.db
    task = models.Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/images")
def images():
    db = models.db
    images = db.session.execute(
        db.select(models.Upload).order_by(models.Upload.filename)
    ).scalars()
    return flask.render_template("images.html", images=images)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = forms.UploadForm()
    db = models.db
    file_ = models.Upload()
    if form.validate_on_submit():
        if form.file.data:
            file_ = models.Upload(
                filename=form.file.data.filename,
                data=form.file.data.read(),
            )
        db.session.add(file_)
        db.session.commit()
        return flask.redirect(flask.url_for("index"))

    return flask.render_template("upload.html", form=form)


@app.route("/upload/<int:file_id>", methods=["GET"])
def get_image(file_id):
    file_ = models.Upload.query.get(file_id)
    if not file_ or not file_.data:
        abort(404, description="File not found")
    return Response(
        file_.data,
        headers={
            "Content-Disposition": f'inline;filename="{file_.filename}"',
            "Content-Type": "application/octet-stream",
        },
    )


if __name__ == "__main__":
    app.run(debug=True)