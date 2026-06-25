import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'unitfire_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unitfire.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'

# Veritabanı Modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='Üye')

# Gömülü Hesap Nesneleri
def get_admin1():
    u = User(id=9991, username="admin1", role="Administrator")
    u.password = generate_password_hash("UnitfireAdmin1!")
    return u

def get_admin2():
    u = User(id=9992, username="admin2", role="Administrator")
    u.password = generate_password_hash("UnitfireAdmin2!")
    return u

@login_manager.user_loader
def load_user(user_id):
    if user_id == "9991": return get_admin1()
    if user_id == "9992": return get_admin2()
    return User.query.get(int(user_id))

# --- ROUTE'LAR ---
@app.route('/')
def home():
    all_users = User.query.all() if current_user.is_authenticated and current_user.role in ['Yönetici', 'Administrator'] else []
    return render_template('index.html', all_users=all_users)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username in ["admin1", "admin2"] or User.query.filter_by(username=username).first():
        flash('Bu kullanıcı adı alınmış veya korumalı.', 'danger')
        return redirect(url_for('home'))
        
    hashed_password = generate_password_hash(password, method='scrypt')
    new_user = User(username=username, password=hashed_password, role='Üye')
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    flash('Hesap başarıyla oluşturuldu!', 'success')
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == "admin1" and password == "UnitfireAdmin1!":
        login_user(get_admin1())
        return redirect(url_for('home'))
    elif username == "admin2" and password == "UnitfireAdmin2!":
        login_user(get_admin2())
        return redirect(url_for('home'))
        
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        flash('Başarıyla giriş yaptınız.', 'success')
    else:
        flash('Hatalı kullanıcı adı veya şifre.', 'danger')
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Oturum kapatıldı.', 'info')
    return redirect(url_for('home'))

@app.route('/update_role', methods=['POST'])
@login_required
def update_role():
    if current_user.role not in ['Yönetici', 'Administrator']:
        flash('Yetkiniz yok.', 'danger')
        return redirect(url_for('home'))
        
    user = User.query.get(request.form.get('user_id'))
    new_role = request.form.get('role')
    
    if user and new_role in ['Üye', 'Yetkili', 'Üst Yetkili', 'Yönetici']:
        user.role = new_role
        db.session.commit()
        flash('Rol güncellendi.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
