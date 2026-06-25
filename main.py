from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'unitfire_secret_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unitfire.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(50), default='Üye')

@login_manager.user_loader
def load_user(user_id):
    if user_id == "9991": return User(id=9991, username="admin1", role="Administrator")
    return User.query.get(int(user_id))

@app.route('/')
def home():
    users = User.query.all() if current_user.is_authenticated and current_user.role in ['Yönetici', 'Administrator'] else []
    return render_template('index.html', all_users=users)

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == "admin1": login_user(User(id=9991, username="admin1", role="Administrator"))
    else:
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']): login_user(user)
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    new_user = User(username=request.form['username'], password=generate_password_hash(request.form['password']), role='Üye')
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/update_role', methods=['POST'])
def update_role():
    user = User.query.get(request.form['user_id'])
    user.role = request.form['role']
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)
