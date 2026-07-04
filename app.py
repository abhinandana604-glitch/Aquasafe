from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from config import Config
from models.user import db, User
from models.patient import Patient

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered!"

        new_user = User(
            full_name=full_name,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:
            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid Email or Password"
        )

    return render_template("login.html")
@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():

    if request.method == "POST":

        patient_name = request.form["patient_name"].strip()
        age = request.form["age"]
        gender = request.form["gender"]
        village = request.form["village"].strip()
        disease = request.form["disease"].strip()
        water_source = request.form["water_source"]
        date_reported = request.form["date_reported"]

        existing_patient = Patient.query.filter_by(
            patient_name=patient_name,
            village=village,
            disease=disease
        ).first()

        if existing_patient:
            return "Patient record already exists!"

        patient = Patient(
            patient_name=patient_name,
            age=age,
            gender=gender,
            village=village,
            disease=disease,
            water_source=water_source,
            date_reported=date_reported
        )

        db.session.add(patient)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("add_patient.html")


@app.route("/patients")
def patients():

    search = request.args.get("search", "")

    if search:
      all_patients = Patient.query.filter(
        (Patient.patient_name.ilike(f"%{search}%")) |
        (Patient.village.ilike(f"%{search}%")) |
        (Patient.disease.ilike(f"%{search}%"))
      ).all()
    else:
        all_patients = Patient.query.all()

    return render_template(
        "patients.html",
        patients=all_patients,
        search=search
    )
@app.route("/dashboard")
def dashboard():

    total_patients = Patient.query.count()

    total_villages = db.session.query(Patient.village).distinct().count()

    total_water_sources = db.session.query(Patient.water_source).distinct().count()

    high_risk_areas = db.session.query(
        Patient.village
    ).group_by(
        Patient.village
    ).having(
        func.count(Patient.id) >= 3
    ).count()

    disease_data = db.session.query(
        Patient.disease,
        func.count(Patient.id).label("total")
    ).group_by(Patient.disease).all()

    village_data = db.session.query(
        Patient.village,
        func.count(Patient.id).label("total")
    ).group_by(Patient.village).all()

    water_source_data = db.session.query(
        Patient.water_source,
        func.count(Patient.id).label("total")
    ).group_by(Patient.water_source).all()

    
    high_risk_villages = db.session.query(
        Patient.village,
        func.count(Patient.id).label("total")
    ).group_by(
        Patient.village
    ).having(
        func.count(Patient.id) >= 3
    ).all()

    return render_template(
        "dashboard.html",
        total_patients=total_patients,
        total_villages=total_villages,
        total_water_sources=total_water_sources,
        high_risk_areas=high_risk_areas,
        disease_data=disease_data,
        village_data=village_data,
        water_source_data=water_source_data,
        high_risk_villages=high_risk_villages
    )

@app.route("/edit_patient/<int:id>", methods=["GET", "POST"])
def edit_patient(id):

    patient = Patient.query.get_or_404(id)

    if request.method == "POST":

        patient.patient_name = request.form["patient_name"]
        patient.age = request.form["age"]
        patient.gender = request.form["gender"]
        patient.village = request.form["village"]
        patient.disease = request.form["disease"]
        patient.water_source = request.form["water_source"]
        patient.date_reported = request.form["date_reported"]

        db.session.commit()

        return redirect(url_for("patients"))

    return render_template(
        "edit_patient.html",
        patient=patient
    )


@app.route("/delete_patient/<int:id>")
def delete_patient(id):

    patient = Patient.query.get_or_404(id)

    db.session.delete(patient)

    db.session.commit()

    return redirect(url_for("patients"))
@app.route("/village")
def village():

    villages = db.session.query(
        Patient.village,
        func.count(Patient.id).label("total")
    ).group_by(
        Patient.village
    ).all()
    high_risk_villages = db.session.query(
        Patient.village,
        func.count(Patient.id).label("total")
    ).group_by(
        Patient.village
    ).having(
        func.count(Patient.id) >= 3
    ).all()

    return render_template(
        "village.html",
        villages=villages
    )
if __name__ == "__main__":
    app.run(debug=True)