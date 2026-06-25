import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'unitfire_super_secret_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unitfire.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Gömülü Admin Kullanıcı Sınıfı
class AdminUser(UserMixin):
    def __init__(self, username):
        self.id = 999  # Sabit ID
        self.username = username
        self.role = 'Administrator'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(50), default='Üye')

@login_manager.user_loader
def load_user(user_id):
    # Gömülü Adminleri yakala
    if user_id == 'admin1_unique': return AdminUser('Administrator1')
    if user_id == 'admin2_unique': return AdminUser('Administrator2')
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form['username'], request.form['password']
    
    # Gömülü Admin Kontrolü
    if u == 'Administrator1' and p == 'Unitfire123!':
        login_user(AdminUser('Administrator1'))
        return redirect(url_for('home'))
    if u == 'Administrator2' and p == 'Unitfire123!':
        login_user(AdminUser('Administrator2'))
        return redirect(url_for('home'))
        
    # Standart Kullanıcı Kontrolü
    user = User.query.filter_by(username=u).first()
    if user and check_password_hash(user.password, p):
        login_user(user)
    return redirect(url_for('home'))

# ... (Diğer fonksiyonlar: register, update_role vs. aynı şekilde kalacak)
