from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'unitfire_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unitfire_studio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Veritabanı Modeli ve Rol Tanımlamaları
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='Üye') # Varsayılan Rol

@login_manager.user_loader
def load_user(user_id):
    # Önce veritabanında ara
    user = User.query.get(int(user_id))
    if user:
        return user
    # Gömülü Administrator hesapları kontrolü
    if user_id == "9991":
        return get_admin1()
    if user_id == "9992":
        return get_admin2()
    return None

# Gömülü Hesap Nesneleri
def get_admin1():
    u = User(id=9991, username="admin1", role="Administrator")
    u.password = generate_password_hash("UnitfireAdmin1!")
    return u

def get_admin2():
    u = User(id=9992, username="admin2", role="Administrator")
    u.password = generate_password_hash("UnitfireAdmin2!")
    return u

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username in ["admin1", "admin2"]:
        flash('Bu kullanıcı adı gömülü sistem tarafından korunmaktadır.', 'danger')
        return redirect(url_for('home'))
        
    user_exists = User.query.filter_by(username=username).first()
    if user_exists:
        flash('Bu kullanıcı adı zaten alınmış.', 'danger')
        return redirect(url_for('home'))
        
    hashed_password = generate_password_hash(password, method='scrypt')
    new_user = User(username=username, password=hashed_password, role='Üye')
    db.session.add(new_user)
    db.session.commit()
    
    flash('Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.', 'success')
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Gömülü Hesap Kontrolleri
    if username == "admin1" and password == "UnitfireAdmin1!":
        login_user(get_admin1())
        flash('Gömülü Administrator olarak giriş yapıldı.', 'success')
        return redirect(url_for('home'))
    elif username == "admin2" and password == "UnitfireAdmin2!":
        login_user(get_admin2())
        flash('Gömülü Administrator olarak giriş yapıldı.', 'success')
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
    # Sadece Yönetici ve Administrator rolündekiler atama yapabilir
    if current_user.role not in ['Yönetici', 'Administrator']:
        flash('Bu işlem için yetkiniz yok.', 'danger')
        return redirect(url_for('home'))
        
    user_id = request.form.get('user_id')
    new_role = request.form.get('role')
    
    if new_role not in ['Üye', 'Yetkili', 'Üst Yetkili', 'Yönetici']:
        flash('Geçersiz rol seçimi.', 'danger')
        return redirect(url_for('home'))
        
    user = User.query.get(user_id)
    if user:
        user.role = new_role
        db.session.commit()
        flash(f'{user.username} adlı kullanıcının rolü {new_role} olarak güncellendi.', 'success')
    else:
        flash('Kullanıcı bulunamadı.', 'danger')
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Veritabanı dosyası yoksa otomatik oluşturur
    app.run(debug=True, host='0.0.0.0', port=5000)
