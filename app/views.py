from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Task
from .forms import NewTaskForm, UpdateTaskForm
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', user=current_user)

@main.route('/terms')
def terms():
    return render_template('terms.html', user=current_user)

@main.route("/loading")
def loading():
    return render_template('loading.html', user=current_user)

@main.route("/dashboard")
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.desc()).all()
    return render_template('dashboard.html', user=current_user, tasks=tasks)

@main.route("/dashboard/in_progress")
def dashboard_in_progress():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.desc()).all()
    return render_template('dashboard_in_progress.html', user=current_user, tasks=tasks)

@main.route("/dashboard/complete")
def dashboard_complete():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.desc()).all()
    return render_template('dashboard_complete.html', user=current_user, tasks=tasks)

@main.route("/task/new", methods=["GET", "POST"])
def new_task():
    form = NewTaskForm()
    if form.validate_on_submit():
        new_task = Task(
            title = form.title.data,
            description = form.description.data,                        
            user_id = current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('new_task.html', user=current_user, form=form)


@main.route("/task/<int:task_id>/update", methods=["GET", "POST"])
@login_required
def update_task(task_id):
    print(f"Updating task with ID: {task_id}")
    task = Task.query.get(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to perform that action.', 'danger')
        return redirect(url_for('main.dashboard'))
    form = UpdateTaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.status = Task.TaskStatus(form.status.data)
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    form.title.data = task.title
    form.description.data = task.description
    form.status.data = task.status.value
    return render_template('update_task.html', user=current_user,  task=task, form=form)


@main.route("/task/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to perform that action.', 'danger')
        return redirect(url_for('main.dashboard'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'error')
    return redirect(url_for('main.dashboard'))
    