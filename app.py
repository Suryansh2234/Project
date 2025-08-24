from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gym.db"
db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50), nullable=False)  # e.g. 3 months
    price = db.Column(db.Float, nullable=False)

# -------------------- AUTH ROUTES --------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# -------------------- DASHBOARD --------------------
@app.route("/dashboard")
def dashboard():
    # if "user_id" not in session:
    #     return redirect(url_for("login"))
    return render_template("dashboard.html")

# -------------------- MEMBER ROUTES --------------------
@app.route("/add_member", methods=["GET","POST"])
def add_member():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        new_member = Member(name=name, age=age, email=email, phone=phone, address=address)
        db.session.add(new_member)
        db.session.commit()
        flash("Member added successfully", "success")
        return redirect(url_for("manage_members"))

    return render_template("add_member.html")

@app.route("/manage_members")
def manage_members():
    members = Member.query.all()
    return render_template("manage_members.html", members=members)

@app.route("/update_member/<int:id>", methods=["GET","POST"])
def update_member(id):
    member = Member.query.get_or_404(id)
    if request.method == "POST":
        member.name = request.form["name"]
        member.age = request.form["age"]
        member.email = request.form["email"]
        member.phone = request.form["phone"]
        member.address = request.form["address"]

        db.session.commit()
        flash("Member updated successfully", "success")
        return redirect(url_for("manage_members"))
    return render_template("update_member.html", member=member)

@app.route("/delete_member/<int:id>")
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash("Member deleted successfully", "success")
    return redirect(url_for("manage_members"))

# -------------------- PLAN ROUTES --------------------
@app.route("/add_plan", methods=["GET","POST"])
def add_plan():
    if request.method == "POST":
        name = request.form["name"]
        duration = request.form["duration"]
        price = request.form["price"]

        new_plan = Plan(name=name, duration=duration, price=price)
        db.session.add(new_plan)
        db.session.commit()
        flash("Plan added successfully", "success")
        return redirect(url_for("manage_plans"))
    return render_template("add_plan.html")

@app.route("/manage_plans")
def manage_plans():
    plans = Plan.query.all()
    return render_template("manage_plans.html", plans=plans)

@app.route("/update_plan/<int:id>", methods=["GET","POST"])
def update_plan(id):
    plan = Plan.query.get_or_404(id)
    if request.method == "POST":
        plan.name = request.form["name"]
        plan.duration = request.form["duration"]
        plan.price = request.form["price"]
        db.session.commit()
        flash("Plan updated successfully", "success")
        return redirect(url_for("manage_plans"))
    return render_template("update_plan.html", plan=plan)

@app.route("/delete_plan/<int:id>")
def delete_plan(id):
    plan = Plan.query.get_or_404(id)
    db.session.delete(plan)
    db.session.commit()
    flash("Plan deleted successfully", "success")
    return redirect(url_for("manage_plans"))

# -------------------- RUN --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


