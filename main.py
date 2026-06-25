import os
fimport os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# --- AYARLAR BÖLÜMÜ (Şifreleri Buradan Güncelle) ---
ADMIN_1_PW = "Unitfire123!"
ADMIN_2_PW = "Unitfire123!"
# ---------------------------------------------------

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'unitfire_2026_secure'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unitfire.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# ... (Modeller ve diğer fonksiyonlar aynı kalıyor)

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    
    # Gömülü Admin Kontrolleri (Ayarlar bölümündeki değişkenleri kullanır)
    if u == 'Administrator1' and p == ADMIN_1_PW: 
        login_user(AdminUser('Administrator1', 9991))
    elif u == 'Administrator2' and p == ADMIN_2_PW: 
        login_user(AdminUser('Administrator2', 9992))
    else:
        user = User.query.filter_by(username=u).first()
        if user and check_password_hash(user.password, p): 
            login_user(user)
    return redirect(url_for('home'))

# ... (Geri kalan kısım aynı)
# --- MODELLER ---
class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(50), default='Üye')

# --- GÖMÜLÜ ADMIN YAPISI ---
class AdminUser(UserMixin):
    def __init__(self, username, id):
        self.username = username
        self.id = id
        self.role = 'Administrator'
    def get_id(self): return f"admin_{self.username}"

@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin_Administrator1": return AdminUser('Administrator1', 9991)
    if user_id == "admin_Administrator2": return AdminUser('Administrator2', 9992)
    return User.query.get(int(user_id))

def add_log(msg):
    db.session.add(SystemLog(message=msg))
    db.session.commit()

# --- ROUTELER ---
@app.route('/')
def home():
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).all() if current_user.is_authenticated and current_user.role != 'Üye' else []
    users = User.query.all() if current_user.is_authenticated and current_user.role in ['Administrator', 'Yönetici'] else []
    return render_template('index.html', logs=logs, all_users=users)

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    # Gömülü Admin Kontrolleri
    if u == 'Administrator1' and p == 'Unitfire123!': login_user(AdminUser('Administrator1', 9991))
    elif u == 'Administrator2' and p == 'Unitfire123!': login_user(AdminUser('Administrator2', 9992))
    else:
        user = User.query.filter_by(username=u).first()
        if user and check_password_hash(user.password, p): login_user(user)
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    u = request.form.get('username')
    if not User.query.filter_by(username=u).first():
        new_user = User(username=u, password=generate_password_hash(request.form.get('password')), role='Üye')
        db.session.add(new_user)
        db.session.commit()
        add_log(f"Yeni kayıt: {u}")
    return redirect(url_for('home'))

@app.route('/update_role', methods=['POST'])
@login_required
def update_role():
    if current_user.role in ['Administrator', 'Yönetici']:
        target = User.query.get(request.form.get('user_id'))
        if target:
            target.role = request.form.get('role')
            db.session.commit()
            add_log(f"{current_user.username} tarafından {target.username} rütbesi {target.role} yapıldı.")
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
