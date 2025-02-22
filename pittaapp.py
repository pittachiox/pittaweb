import os
import flask
import models
import forms
from flask_login import login_required, login_user, logout_user, LoginManager, current_user
from flask import render_template, redirect, url_for, Response, flash, request, abort
from models import db, User, Upload, Task, Role, UserProfile
from werkzeug.utils import secure_filename
from forms import TaskForm


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
models.init_app(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

@app.route("/")
@login_required  # ป้องกันไม่ให้เข้าถึงได้หากยังไม่ได้ล็อกอิน
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
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
            try:
                user = User(username=form.username.data, name=form.name.data)
                user.password_hash = form.password.data  # ✅ ใช้ setter ของ password

                db.session.add(user)
                db.session.commit()  # ✅ บันทึก user ก่อน เพื่อให้มี ID

                # ✅ เพิ่ม role หลังจากบันทึก user แล้ว
                role = Role.query.filter_by(name="user").first()
                if not role:
                    role = Role(name="user")
                    db.session.add(role)
                    db.session.commit()  # ✅ บันทึก role ก่อน

                user.roles.append(role)  # ✅ ตอนนี้ user มี ID แล้ว
                db.session.commit()  # ✅ บันทึกอีกครั้ง

                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("login"))

            except Exception as e:
                db.session.rollback()  # ✅ ป้องกันข้อมูลเสียหายถ้าเกิด error
                print(f"Error: {e}")
                flash("An error occurred during registration.", "danger")

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
    current_user.profile.nickname = request.form.get('nickname')
    current_user.profile.faculty = request.form.get('faculty')
    current_user.profile.student_id = request.form.get('student_id')
    current_user.profile.emoji = request.form.get('profile_emoji')  # รับค่าอิโมจิที่เลือก
    db.session.commit()

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('images'))

    # ตรวจสอบว่ามีโปรไฟล์อยู่แล้วหรือไม่ ถ้าไม่มีให้สร้างใหม่
    if not current_user.profile:
        current_user.profile = UserProfile(user_id=current_user.id)

    # อัปเดตข้อมูลในโปรไฟล์
    current_user.profile.nickname = nickname
    current_user.profile.faculty = faculty
    current_user.profile.student_id = student_id

    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for("images"))



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
        abort(403)  # ถ้าไม่ใช่เจ้าของ task
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully!", "success")  # แจ้งเตือนเมื่อมีการลบ
    return redirect(url_for("index"))


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = forms.UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file.filename == '':
            flash("No selected file", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file.seek(0)  # ✅ รีเซ็ต pointer ก่อนอ่านข้อมูล
        uploaded_file = Upload(filename=filename, data=file.read())
        db.session.add(uploaded_file)
        db.session.commit()

        flash("File uploaded successfully!", "success")
        return redirect(url_for("images"))
    return render_template("upload.html", form=form)

@app.route("/images")
@login_required
def images():
    user = User.query.get(current_user.id)
    return render_template("profile.html", user=user, profile=user.profile)



@app.route("/upload/<int:file_id>")
@login_required
def get_uploaded_image(file_id):
    file_ = Upload.query.get_or_404(file_id)
    return Response(file_.data, headers={"Content-Disposition": f'inline;filename="{file_.filename}"', "Content-Type": "application/octet-stream"})

@app.route("/calendar")
@login_required
def calendar():
    return render_template("calendar.html")


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
@login_required
def mark_complete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)  # ป้องกันไม่ให้ผู้ใช้คนอื่นแก้ไข task ของคนอื่น
    task.status = "Completed"
    db.session.commit()
    flash("Task marked as completed!", "success")
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/update", methods=["GET", "POST"])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)  # ป้องกันผู้ใช้ที่ไม่ใช่เจ้าของ task

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data  # ✅ บันทึกค่าใหม่
        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for("index"))

    print(form.errors)  # ✅ Debug form errors
    return render_template("update_task.html", form=form, task=task)


@app.route("/tasks/<int:task_id>/toggle_complete", methods=["POST"])
@login_required
def toggle_complete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    
    # สลับสถานะระหว่าง 'Completed' และ 'Pending'
    task.status = "Pending" if task.status == "Completed" else "Completed"
    db.session.commit()
    flash("Task status updated!", "success")
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)