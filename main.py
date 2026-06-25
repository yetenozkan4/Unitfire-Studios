from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'unitfire_secret_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unitfire_studio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'

# --- MODEL ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='Üye')

# --- YARDIMCI FONKSİYONLAR ---
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
    users = []
    if current_user.is_authenticated and current_user.role in ['Yönetici', 'Administrator']:
        users = User.query.all()
    return render_template('index.html', all_users=users)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Admin girişleri
    if username == "admin1" and password == "UnitfireAdmin1!":
        login_user(get_admin1())
    elif username == "admin2" and password == "UnitfireAdmin2!":
        login_user(get_admin2())
    else:
        # Normal kullanıcı girişi
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    if not User.query.filter_by(username=username).first() and username not in ["admin1", "admin2"]:
        new_user = User(username=username, password=generate_password_hash(password), role='Üye')
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
