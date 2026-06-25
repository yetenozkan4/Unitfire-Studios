import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'unitfire_super_secret_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unitfire.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Log Tablosu
class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(50), default='Üye')

@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

def add_log(msg):
    db.session.add(SystemLog(message=msg))
    db.session.commit()

@app.route('/')
def home():
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).all() if current_user.is_authenticated and current_user.role != 'Üye' else []
    users = User.query.all() if current_user.is_authenticated and current_user.role in ['Administrator', 'Yönetici'] else []
    return render_template('index.html', logs=logs, all_users=users)

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username']).first()
    if user and check_password_hash(user.password, request.form['password']):
        login_user(user)
        add_log(f"{user.username} sisteme giriş yaptı.")
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    new_user = User(username=request.form['username'], password=generate_password_hash(request.form['password']), role='Üye')
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    add_log(f"Yeni üye kaydı: {new_user.username}")
    return redirect(url_for('home'))

@app.route('/update_role', methods=['POST'])
@login_required
def update_role():
    if current_user.role in ['Administrator', 'Yönetici']:
        target = User.query.get(request.form['user_id'])
        target.role = request.form['role']
        db.session.commit()
        add_log(f"ADMIN {current_user.username}: {target.username} kullanıcısını {target.role} yaptı.")
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)
