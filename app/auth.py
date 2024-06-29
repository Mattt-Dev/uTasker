from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import check_password_hash
from . import db, mail
from .models import User
from flask_mail import Message
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegistrationForm, PasswordResetRequestForm, EditProfileForm, ResetPasswordForm
from itsdangerous import URLSafeTimedSerializer as Serializer
from smtplib import SMTPAuthenticationError


auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email = form.email.data).first()
        if existing_user:
            flash('Email already exists.', 'danger')
        else:
            user = User(username = form.username.data, email = form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.loading'))
    return render_template('register.html', form=form, user=current_user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully !")
            return redirect(url_for('main.loading'))
        else:
            flash("Incorrect credentials. Please try again.", "error")
    return render_template('login.html', form = form, user = current_user)

@auth.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            flash('An email has been sent with instructions to reset your password. ', 'info')
            send_password_reset_email(user)
            return redirect(url_for('main.loading'))
        else:
            flash('Email does not exist.', 'danger')
    return render_template('password_reset_request.html', user=current_user, form = form)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    msg = Message('uTasker - Reset your password', recipients=[user.email])
    msg.body = f"We received a request to reset the password for your account. ''\nIn order to do that, please visit the following link: {url_for('auth.reset_password', token=token, _external=True)}.\nIf you did not request a password reset, please ignore this email."
    try:
        mail.send(msg)
    except SMTPAuthenticationError:
        flash('There was an error sending the email. Please try again.', 'danger')

@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email        
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match.' , 'error')
            return redirect(url_for('auth.edit_profile'))
        user = User.query.filter_by(email=current_user.email).first()
        user.username = form.username.data
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('main.loading'))
    return render_template('edit_profile.html', form = form, user = current_user)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.loading'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.loading'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been reset.', 'success')
            return redirect(url_for('auth.login'))
        except:
            flash('There was an error resetting your password. Please try again.', 'danger')
    return render_template('reset_password.html', form = form, user = current_user)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.loading'))