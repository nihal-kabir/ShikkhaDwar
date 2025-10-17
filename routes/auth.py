from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from datetime import datetime, timezone
from constants import TEMPLATE_LOGIN, TEMPLATE_REGISTER, ROLE_STUDENT, ROLE_INSTRUCTOR

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form.get('role', ROLE_STUDENT)  # Get role from form, default to student

        # Validate role
        if role not in [ROLE_STUDENT, ROLE_INSTRUCTOR]:
            role = ROLE_STUDENT

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template(TEMPLATE_REGISTER)

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template(TEMPLATE_REGISTER)

        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template(TEMPLATE_REGISTER)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template(TEMPLATE_LOGIN)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        # Update user information
        user.first_name = request.form.get('first_name', user.first_name)
        user.last_name = request.form.get('last_name', user.last_name)

        # Check if email is being changed
        new_email = request.form.get('email')
        if new_email and new_email != user.email:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != user.id:
                flash('Email already in use by another account.', 'error')
                return render_template('auth/profile.html', user=user)
            user.email = new_email

        # Update password if provided
        new_password = request.form.get('new_password')
        current_password = request.form.get('current_password')

        if new_password:
            # Verify current password
            if not current_password or not check_password_hash(user.password_hash, current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('auth/profile.html', user=user)

            # Update to new password
            user.password_hash = generate_password_hash(new_password)

        try:
            db.session.commit()

            # Update session if username display name changed
            session['username'] = user.username

            if new_password:
                flash('Profile and password updated successfully!', 'success')
            else:
                flash('Profile updated successfully!', 'success')

            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')

    return render_template('auth/profile.html', user=user)