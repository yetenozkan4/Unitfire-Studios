import os
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'unitfire_secret_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unitfire.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='Üye')

def get_admin(id, name, pwd):
    u = User(id=id, username=name, role="Administrator")
    u.password = generate_password_hash(pwd)
    return u

@login_manager.user_loader
def load_user(user_id):
    if user_id == "9991": return get_admin(9991, "admin1", "UnitfireAdmin1!")
    if user_id == "9992": return get_admin(9992, "admin2", "UnitfireAdmin2!")
    return User.query.get(int(user_id))

@app.route('/')
def home():
    users = User.query.all() if current_user.is_authenticated and current_user.role in ['Yönetici', 'Administrator'] else []
    return render_template('index.html', all_users=users)

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    # Admin girişleri
    if u == "admin1" and p == "UnitfireAdmin1!": login_user(get_admin(9991, u, p))
    elif u == "admin2" and p == "UnitfireAdmin2!": login_user(get_admin(9992, u, p))
    else:
        # Kayıt veya giriş denemesi (Basit mantık: Varsa giriş yap, yoksa yeni kayıt oluştur)
        user = User.query.filter_by(username=u).first()
        if user:
            if check_password_hash(user.password, p): login_user(user)
        else:
            # Kullanıcı yoksa otomatik kayıt
            new_user = User(username=u, password=generate_password_hash(p), role='Üye')
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
    return redirect(url_for('home'))

@app.route('/update_role', methods=['POST'])
@login_required
def update_role():
    if current_user.role in ['Yönetici', 'Administrator']:
        user = User.query.get(request.form.get('user_id'))
        if user:
            user.role = request.form.get('role')
            db.session.commit()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
