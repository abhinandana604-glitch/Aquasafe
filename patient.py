from models.user import db


class Patient(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    patient_name = db.Column(db.String(100), nullable=False)

    age = db.Column(db.Integer, nullable=False)

    gender = db.Column(db.String(20), nullable=False)

    village = db.Column(db.String(100), nullable=False)

    disease = db.Column(db.String(100), nullable=False)

    water_source = db.Column(db.String(100), nullable=False)

    date_reported = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Patient {self.patient_name}>"