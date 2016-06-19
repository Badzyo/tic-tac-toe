from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from app.models import User
from app import forms


@app.route("/")
@login_required
def index():
    user = current_user
    return render_template('index.html', user=user)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        form = forms.LoginForm(request.form)
    else:
        form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.get_authenticated_user(form.username.data, form.password.data)
        if user:
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html', login_form=form)


@app.route("/logout", methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = forms.RegisterForm(request.form)
    else:
        form = forms.RegisterForm()

    if form.validate_on_submit():
        user = User(form.username.data, form.password.data, form.email.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return render_template('register.html', register_form=form)

