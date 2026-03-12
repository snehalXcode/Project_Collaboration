import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from database.db_connection import db, init_app as init_db
from model.cnn_model import load_or_build_model, predict_embedding
from model.preprocess import (
    compute_image_hash,
    prepare_for_model,
    preprocess_image,
    read_image_file,
)


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()  # Load DB_* and other environment variables if present.


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # Initialize database (MySQL via SQLAlchemy).
    init_db(app)

    # Import models after db has been set up.
    from database.models import Animal, MedicalRecord, Adopter, AdoptionRequest, Donation  # noqa: F401

    with app.app_context():
        db.create_all()

    # Lazy-load the CNN model once per process.
    cnn_model = load_or_build_model()

    # -------------------- Web Pages --------------------

    @app.route("/")
    def index():
        animals = Animal.query.filter_by(adoption_status="available").order_by(
            Animal.created_at.desc()
        ).limit(12)
        return render_template("index.html", animals=animals)

    @app.route("/dashboard")
    def dashboard():
        animals = Animal.query.order_by(Animal.created_at.desc()).all()
        return render_template("dashboard.html", animals=animals)

    @app.route("/animal/<int:animal_id>")
    def animal_profile(animal_id: int):
        animal = Animal.query.get_or_404(animal_id)
        medical_records = MedicalRecord.query.filter_by(animal_id=animal.id).order_by(
            MedicalRecord.record_date.desc()
        )
        return render_template(
            "animal_profile.html",
            animal=animal,
            medical_records=medical_records,
        )

    @app.route("/adopt")
    def adoption_list():
        animals = Animal.query.filter_by(adoption_status="available").order_by(
            Animal.created_at.desc()
        )
        return render_template("adoption_list.html", animals=animals)

    @app.route("/donate")
    def donate_page():
        return render_template("donate.html")

    # -------------------- API: Animals --------------------

    @app.post("/api/animals")
    def api_add_animal():
        """
        Add a new animal record (without necessarily uploading an image).
        """
        data = request.json or {}

        animal = Animal(
            animal_id=data.get("animal_id") or f"AN-{int(datetime.utcnow().timestamp())}",
            species=data.get("species"),
            breed=data.get("breed"),
            rescue_date=data.get("rescue_date"),
            shelter_location=data.get("shelter_location"),
            health_status=data.get("health_status") or "Unknown",
        )
        db.session.add(animal)
        db.session.commit()

        return jsonify({"status": "success", "animal_id": animal.id}), 201

    @app.get("/api/animals")
    def api_get_animals():
        """
        Retrieve animal records with basic search by species, breed, or shelter location.
        """
        from database.models import Animal  # local import for type hints

        query = Animal.query
        species = request.args.get("species")
        breed = request.args.get("breed")
        shelter = request.args.get("shelter_location")

        if species:
            query = query.filter(Animal.species.ilike(f"%{species}%"))
        if breed:
            query = query.filter(Animal.breed.ilike(f"%{breed}%"))
        if shelter:
            query = query.filter(Animal.shelter_location.ilike(f"%{shelter}%"))

        animals = query.order_by(Animal.created_at.desc()).all()
        return jsonify([a.to_dict() for a in animals])

    @app.put("/api/animals/<int:animal_id>")
    def api_update_animal(animal_id: int):
        """
        Update health status or basic details for an animal.
        """
        animal = Animal.query.get_or_404(animal_id)
        data = request.json or {}

        for field in [
            "species",
            "breed",
            "rescue_date",
            "shelter_location",
            "health_status",
            "adoption_status",
        ]:
            if field in data:
                setattr(animal, field, data[field])

        db.session.commit()
        return jsonify({"status": "success", "animal": animal.to_dict()})

    # -------------------- API: Upload & Recognition --------------------

    @app.post("/api/animals/upload")
    def api_upload_and_recognize():
        """
        Upload an animal image, preprocess, and check if it already exists.
        - If image hash matches an existing animal: return that record.
        - Otherwise, create a new record with minimal info and return it.
        """
        from database.models import Animal

        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image file provided."}), 400

        # Read + preprocess image.
        image_bgr = read_image_file(file)
        preprocessed = preprocess_image(image_bgr)
        image_hash = compute_image_hash(preprocessed)
        batch = prepare_for_model(preprocessed)

        # Optional: get an embedding/prediction from the CNN (starter only).
        _embedding = predict_embedding(cnn_model, batch)

        # Check if this exact image hash exists.
        existing = Animal.query.filter_by(image_hash=image_hash).first()
        if existing:
            return jsonify(
                {
                    "status": "existing",
                    "animal": existing.to_dict(),
                }
            )

        # Save the uploaded file to disk.
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{file.filename}"
        save_path = UPLOAD_DIR / filename
        # We already consumed the stream to preprocess; rewind to save.
        file.stream.seek(0)
        file.save(save_path)

        # Create a lightweight placeholder record; NGO staff can update details later.
        new_animal = Animal(
            animal_id=f"AN-{int(datetime.utcnow().timestamp())}",
            species="Unknown",
            breed="Unknown",
            rescue_date=datetime.utcnow().date(),
            shelter_location="Unknown",
            health_status="Unknown",
            image_filename=filename,
            image_hash=image_hash,
        )
        db.session.add(new_animal)
        db.session.commit()

        return jsonify(
            {
                "status": "new",
                "animal": new_animal.to_dict(),
            }
        ), 201

    # -------------------- API: Adoption --------------------

    @app.post("/api/adoption_requests")
    def api_adoption_request():
        """
        Create a new adoption request for an animal.
        """
        data = request.json or {}
        animal_id = data.get("animal_id")
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        address = data.get("address")
        message = data.get("message")

        if not all([animal_id, name, email]):
            return jsonify({"error": "animal_id, name and email are required."}), 400

        animal = Animal.query.get_or_404(animal_id)

        adopter = Adopter(name=name, email=email, phone=phone, address=address)
        db.session.add(adopter)
        db.session.flush()  # get adopter.id

        req = AdoptionRequest(
            animal_id=animal.id,
            adopter_id=adopter.id,
            message=message,
        )
        db.session.add(req)
        db.session.commit()

        return jsonify({"status": "success", "request_id": req.id}), 201

    # -------------------- API: Donations --------------------

    @app.post("/api/donations")
    def api_donation():
        """
        Store a simple donation record.
        """
        data = request.json or {}
        donor_name = data.get("donor_name")
        amount = data.get("amount")

        if not donor_name or amount is None:
            return jsonify({"error": "donor_name and amount are required."}), 400

        donation = Donation(
            donor_name=donor_name,
            donor_email=data.get("donor_email"),
            amount=amount,
            message=data.get("message"),
        )
        db.session.add(donation)
        db.session.commit()

        return jsonify({"status": "success", "donation_id": donation.id}), 201

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

