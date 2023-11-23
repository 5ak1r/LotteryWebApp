# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from app import db, requires_roles
from models import User
from users.forms import RegisterForm, LoginForm, PasswordForm
from markupsafe import Markup
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
import logging

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        # admin registration screen creates new admin, else user
        try:
            if current_user.role == 'admin':
                role='admin'
            else:
                role='user'
        except:
            role='user'

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        dob=form.dob.data,
                        postcode=form.postcode.data,
                        password=form.password.data,
                        role=role)

        logging.warning('SECURITY - User Registration [%s, %s]',
                        form.email.data,
                        request.remote_addr)
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        session['email'] = new_user.email
        # sends user to set up 2-factor authentication; sends admin back to admin page
        if role == 'user':
            return redirect(url_for('users.setup_2fa'))
        elif role == 'admin':
            flash("New admin registered successfully")
            return redirect(url_for('admin.admin'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_anonymous:
        form = LoginForm()

        # begin counting login attempts, user has 3 before they are redirected
        if not session.get('authentication_attempts'):
            session['authentication_attempts'] = 0

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            if not user or not user.verify_password(form.password.data) or not user.verify_pin(form.pin.data) or not user.verify_postcode(form.postcode.data):
                # failed login, -1 attempts left
                session['authentication_attempts'] += 1
                logging.warning('SECURITY - Failed Login [%s, %s]',
                                form.email.data,
                                request.remote_addr)
                if session.get('authentication_attempts') >= 3:
                    flash(Markup('Number of incorrect login attempts exceeded. Please click <a href="/reset">here</a> to reset.'))
                    return render_template('users/login.html')
                flash(f"Please check your login details and try again, {3 - session['authentication_attempts']} login {'attempts' if 3 - session['authentication_attempts'] != 1 else 'attempt'} remaining.")
                return render_template('users/login.html', form=form)
            else:
                # successful login
                login_user(user)

                logging.warning('SECURITY - Log In [%s, %s, %s]',
                                current_user.id,
                                current_user.email,
                                request.remote_addr)
                
                # storing information about current and last logins to the database
                current_user.last_login = current_user.current_login
                current_user.ip_last = current_user.ip_current
                current_user.current_login = datetime.now()
                current_user.ip_current = request.remote_addr

                current_user.successful_logins += 1

                db.session.commit()
                # remove attempts after successful login
                del session['authentication_attempts']

                # redirects admin to the admin page; user to lottery page
                if current_user.role == "admin":
                    return redirect(url_for('admin.admin'))
                else:
                    return redirect(url_for('lottery.lottery'))
        elif request.method == 'POST' and not form.recaptcha.data:
            flash("Please complete the reCAPTCHA")

        return render_template('users/login.html', form=form)
    else:
        flash("You are already logged in.")
        return render_template('main/index.html')

@users_blueprint.route('/logout')
def logout():
    logout_user()

    logging.warning('SECURITY - Log Out [%s, %s, %s]',
                                current_user.id,
                                current_user.email,
                                request.remote_addr)
    
    return render_template('main/index.html')


@users_blueprint.route('/reset')
def reset():
    session['authentication_attempts'] = 0
    return redirect(url_for('users.login'))


# view user account
@users_blueprint.route('/account')
@login_required
@requires_roles('user', 'admin')
def account():
    return render_template('users/account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone,
                           dob=current_user.dob,
                           postcode=current_user.postcode)


@users_blueprint.route('/setup_2fa')
def setup_2fa():
    if 'email' not in session:
        return redirect(url_for('main.index'))
    user = User.query.filter_by(email=session['email']).first()

    if not user:
        return redirect(url_for('main.index'))

    del session['email']

    return render_template('users/setup_2fa.html', email=user.email, uri=user.get_2fa_uri()), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }


@users_blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = PasswordForm()

    if form.validate_on_submit():

        if form.current_password.data == current_user.password:
            if form.new_password.data != current_user.password:
                current_user.password = form.new_password.data
                db.session.commit()
                flash('Password changed successfully')
            else:
                flash('New password matches old password')
        else:
            flash('Current password entered incorrectly')

        return redirect(url_for('users.account'))

    return render_template('users/change_password.html', form=form)