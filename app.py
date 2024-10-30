from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import requests
import os

from decorators import admin_required
from models import db, User

#region setup
app = Flask(__name__)
app.config['DEBUG'] = True

app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

FASTAPI_URL = "http://127.0.0.1:8000"

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'error'
#endregion

#region Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = request.form.get('is_admin') == 'on'  # Checkbox for admin

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))

        flash('Invalid username or password.','error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
#endregion

#region Cryptids
@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/')
@login_required
def index():
    response = requests.get(f"{FASTAPI_URL}/cryptids/")
    cryptids = response.json()
    return render_template("index.html", cryptids=cryptids)

@app.route('/cryptid/<int:cryptid_id>')
@login_required
def cryptid_detail(cryptid_id):
    response = requests.get(f"{FASTAPI_URL}/cryptids/{cryptid_id}")
    cryptid = response.json()
    return render_template("cryptid.html", cryptid=cryptid)

@app.route('/add', methods=['GET','POST'])
@login_required
def add_cryptid():
    if request.method == 'POST':
        name=request.form['name']
        description = request.form['description']
        image_url = request.form['image_url']

        new_cryptid = {
            "name":name,
            "description": description,
            "image_url":image_url
        }
        print(new_cryptid)
        
        response = requests.post(f"{FASTAPI_URL}/cryptids/", json=new_cryptid)

        if response.status_code == 201:
            flash("Cryptid added successfully!", 'success')
            return redirect(url_for('index'))
        else:
            flash("An error has occured while adding the cryptid.", 'error')
    return render_template("add_cryptid.html")

@app.route('/cryptid/<int:cryptid_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cryptid(cryptid_id):
    if request.method == 'POST':
        updated_cryptid = {
            "name": request.form['name'],
            "description": request.form['description'],
            "image_url": request.form['image_url']
        }

        response = requests.put(f"{FASTAPI_URL}/cryptids/{cryptid_id}", json=updated_cryptid)
        
        if response.status_code == 201:
            flash("Cryptid updated successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Failed to update the cryptid. Please try again.", "error")
            return redirect(url_for('edit_cryptid', cryptid_id=cryptid_id))

    response = requests.get(f"{FASTAPI_URL}/cryptids/{cryptid_id}")
    
    if response.status_code == 200:
        cryptid = response.json()
        return render_template('edit_cryptid.html', cryptid=cryptid)
    else:
        flash("Cryptid not found.", "error")
        return redirect(url_for('index'))
    
@app.route('/cryptid/<int:cryptid_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_cryptid(cryptid_id):
    response = requests.delete(f"{FASTAPI_URL}/cryptids/{cryptid_id}")

    if response.status_code == 204:
        flash("Cryptid deleted successfully!", "success")
    else:
        flash("Failed to delete the cryptid. Please try again.", "error")

    return redirect(url_for('index'))
#endregion

if __name__ == "__main__":
    app.run(debug=True)
