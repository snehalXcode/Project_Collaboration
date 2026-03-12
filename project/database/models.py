from datetime import datetime

from database.db_connection import db


class Animal(db.Model):
    __tablename__ = "animals"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.String(64), unique=True, nullable=False)
    species = db.Column(db.String(100))
    breed = db.Column(db.String(150))
    rescue_date = db.Column(db.Date)
    shelter_location = db.Column(db.String(255))
    health_status = db.Column(db.String(255))
    image_filename = db.Column(db.String(255))
    image_hash = db.Column(db.String(64), index=True)
    adoption_status = db.Column(
        db.Enum("available", "adopted", "not_available", name="adoption_status_enum"),
        default="available",
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    medical_records = db.relationship(
        "MedicalRecord", backref="animal", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "animal_id": self.animal_id,
            "species": self.species,
            "breed": self.breed,
            "rescue_date": self.rescue_date.isoformat() if self.rescue_date else None,
            "shelter_location": self.shelter_location,
            "health_status": self.health_status,
            "image_filename": self.image_filename,
            "adoption_status": self.adoption_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MedicalRecord(db.Model):
    __tablename__ = "medical_records"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animals.id"), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    treatment = db.Column(db.Text)
    vet_name = db.Column(db.String(255))


class Adopter(db.Model):
    __tablename__ = "adopters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    adoption_requests = db.relationship(
        "AdoptionRequest",
        backref="adopter",
        lazy=True,
        cascade="all, delete-orphan",
    )


class AdoptionRequest(db.Model):
    __tablename__ = "adoption_requests"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animals.id"), nullable=False)
    adopter_id = db.Column(db.Integer, db.ForeignKey("adopters.id"), nullable=False)
    status = db.Column(
        db.Enum("pending", "approved", "rejected", name="adoption_status_request_enum"),
        default="pending",
        nullable=False,
    )
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.Text)

    animal = db.relationship("Animal", backref=db.backref("adoption_requests", lazy=True))


class Donation(db.Model):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(255), nullable=False)
    donor_email = db.Column(db.String(255))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

