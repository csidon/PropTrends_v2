# Contains all the routes specific to users - register, login, logout, account

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from proptrends import db, bcrypt
from proptrends.models import User
from proptrends.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
from proptrends.users.utils import saveImage

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()

    if form.validate_on_submit():
        # Using Bcrypt to hash the password so that we don't store passwords in plain text
        hashedPW = bcrypt.generate_password_hash(form.user_password.data).decode('utf-8')
        # Create an object user with the data collected from the form, passing in the hashed password (instead of cleartext) 
        user = User(user_email=form.user_email.data, user_last_name=form.user_last_name.data, user_first_name=form.user_first_name.data, user_password=hashedPW)
        db.session.add(user)        # Adds user to db
        db.session.commit()         # Commits user to db
        flash('Your account has been created. Please log into your account', 'success')
        return redirect(url_for('users.login'))

    errors = [{'field': key, 'messages': form.errors[key]} for key in form.errors.keys()] if form.errors else []
    return render_template('register.html', title='Alpha Invite Members Only', form=form, errors=errors)

@users.route("/login", methods=['GET','POST'])
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.user_email.data).first()
        # Decrypt the password hash and check it against the users' password in the database
        # If they match, log the user in and remember their "remember me " choice
        if user and bcrypt.check_password_hash(user.user_password, form.user_password.data):
            login_user(user, remember=form.user_remember.data)
            # If the user has been trying to access a specific page before logging in, redirect them to that page. Otherwise redirect them to home
            nextPage = request.args.get('next')
            return redirect(nextPage) if nextPage else redirect(url_for('main.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
            return render_template('login.html', title='Log into your PropTrends Account!', form=form)       
    return render_template('login.html', title='Log into your Proptrends Account!', form=form)


@users.route("/logout")
def logout():
    # Uses flask-login's logout_user function
    logout_user()
    return redirect(url_for('main.home')) 

@users.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.upload_image.data:
            # Saving the picture and updating the database with the hex-ed filename
            hexedImage = saveImage(form.upload_image.data)
            current_user.user_image = hexedImage

        current_user.user_first_name = form.user_first_name.data
        current_user.user_last_name = form.user_last_name.data
        current_user.user_email = form.user_email.data

        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.user_first_name.data = current_user.user_first_name
        form.user_last_name.data = current_user.user_last_name
        form.user_email.data = current_user.user_email

    user_image = url_for('static', filename='profilePics/' + current_user.user_image)
    return render_template('account.html', title='Your Proptrends User Account', user_image=user_image, form=form)