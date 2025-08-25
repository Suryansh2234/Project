from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200), nullable=False)
   

class MembershipPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    members = db.relationship('Member', backref='plan', lazy=True)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('membership_plan.id'), nullable=False)
    joining_date = db.Column(db.Date, nullable=False)

# Authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if Admin.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        admin = Admin(username=username, password=hashed_pw)
        db.session.add(admin)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/')
def index():
    return render_template('index.html')


# Member Management
@app.route('/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    plans = MembershipPlan.query.all()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']
        plan_id = request.form['plan_id']
        joining_date = request.form['joining_date']
        member = Member(name=name, age=age, gender=gender, contact=contact, plan_id=plan_id, joining_date=datetime.strptime(joining_date, '%Y-%m-%d'))
        db.session.add(member)
        db.session.commit()
        flash('Member added successfully.', 'success')
        return redirect(url_for('members'))
    return render_template('add_member.html', plans=plans)

@app.route('/members')
@login_required
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)

@app.route('/update_member/<int:id>', methods=['GET', 'POST'])
@login_required
def update_member(id):
    member = Member.query.get_or_404(id)
    plans = MembershipPlan.query.all()
    if request.method == 'POST':
        member.name = request.form['name']
        member.age = request.form['age']
        member.gender = request.form['gender']
        member.contact = request.form['contact']
        member.plan_id = request.form['plan_id']
        member.joining_date = datetime.strptime(request.form['joining_date'], '%Y-%m-%d')
        db.session.commit()
        flash('Member updated successfully.', 'success')
        return redirect(url_for('members'))
    return render_template('update_member.html', member=member, plans=plans)

@app.route('/delete_member/<int:id>')
@login_required
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted.', 'success')
    return redirect(url_for('members'))

# Membership Plan Management
@app.route('/add_plan', methods=['GET', 'POST'])
@login_required
def add_plan():
    if request.method == 'POST':
        name = request.form['name']
        duration = request.form['duration']
        price = request.form['price']
        plan = MembershipPlan(name=name, duration=duration, price=price)
        db.session.add(plan)
        db.session.commit()
        flash('Plan added successfully.', 'success')
        return redirect(url_for('plans'))
    return render_template('add_plan.html')

@app.route('/plans')
@login_required
def plans():
    plans = MembershipPlan.query.all()
    return render_template('plans.html', plans=plans)

@app.route('/update_plan/<int:id>', methods=['GET', 'POST'])
@login_required
def update_plan(id):
    plan = MembershipPlan.query.get_or_404(id)
    if request.method == 'POST':
        plan.name = request.form['name']
        plan.duration = request.form['duration']
        plan.price = request.form['price']
        db.session.commit()
        flash('Plan updated successfully.', 'success')
        return redirect(url_for('plans'))
    return render_template('update_plan.html', plan=plan)

@app.route('/delete_plan/<int:id>')
@login_required
def delete_plan(id):
    plan = MembershipPlan.query.get_or_404(id)
    db.session.delete(plan)
    db.session.commit()
    flash('Plan deleted.', 'success')
    return redirect(url_for('plans'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
