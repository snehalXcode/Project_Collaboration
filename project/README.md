Integrated NGO Platform for Animal Rescue, Identification, Virtual Adoption and Donation
=======================================================================================

This is a starter Flask web application that demonstrates an **integrated NGO platform** for:

- Animal rescue and centralized record management
- AI-based image recognition for identifying rescued animals
- Virtual adoption workflows
- Donation tracking

The stack uses **Flask (Python)**, **MySQL**, **TensorFlow (CNN)**, and **OpenCV** for image preprocessing.


Project Structure
-----------------

```text
project/
├── app.py
├── requirements.txt
├── model/
│   ├── cnn_model.py
│   └── preprocess.py
├── database/
│   ├── db_connection.py
│   └── schema.sql
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── animal_profile.html
│   ├── adoption_list.html
│   └── donate.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
├── uploads/
│   └── .gitkeep
└── sample_data/
    ├── animals_sample.csv
    └── README.md
```


Prerequisites
-------------

- Python 3.10+ (3.12 is fine)
- MySQL server running locally
- `pip` for installing dependencies


MySQL Setup
-----------

1. Log into MySQL and create a database:

```sql
CREATE DATABASE ngo_animals CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Create a user (or reuse an existing one) and grant permissions:

```sql
CREATE USER 'ngo_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON ngo_animals.* TO 'ngo_user'@'localhost';
FLUSH PRIVILEGES;
```

3. Load the schema:

```bash
cd "c:\Users\Snehal\Documents\Project collabration tool\project"
mysql -u ngo_user -p ngo_animals < database/schema.sql
```


Python Environment Setup
------------------------

From the `project` directory:

```bash
cd "c:\Users\Snehal\Documents\Project collabration tool\project"

# (Optional) create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```


Configuration
-------------

The Flask app reads database configuration from environment variables, with sensible defaults:

- `DB_USER` (default: `ngo_user`)
- `DB_PASSWORD` (default: `strong_password_here`)
- `DB_HOST` (default: `localhost`)
- `DB_NAME` (default: `ngo_animals`)

You can create a `.env` file or set these in your terminal before running:

```bash
set DB_USER=ngo_user
set DB_PASSWORD=strong_password_here
set DB_HOST=localhost
set DB_NAME=ngo_animals
```


Running the Application Locally
-------------------------------

From the `project` directory:

```bash
cd "c:\Users\Snehal\Documents\Project collabration tool\project"
venv\Scripts\activate  # if you created a venv
set FLASK_APP=app.py
set FLASK_ENV=development
python app.py
```

Then open `http://127.0.0.1:5000/` in your browser.


Basic Flow
----------

1. **NGO Dashboard (`/dashboard`)**
   - Add a new rescued animal (with or without an image).
   - Upload an animal image for recognition.
   - View and search existing animal records.
   - Update health status and medical notes.

2. **Image Recognition**
   - User uploads an image through the dashboard.
   - Image is preprocessed with OpenCV (resize, normalization).
   - A simple CNN model (TensorFlow) is loaded to generate an embedding (starter, not trained).
   - A hash of the preprocessed image is stored in the `animals` table.
   - If the hash already exists, the existing animal record is returned.
   - If not, the app creates a new record with status `Unknown` species/breed (you can update it later).

3. **Virtual Adoption (`/adopt`)**
   - Public page listing animals marked as `available` for adoption.
   - View individual animal profile.
   - Submit an adoption request (stored in `adoption_requests` table).

4. **Donations (`/donate`)**
   - Simple donation form that stores donor information and donation amount in the `donations` table.


Sample Dataset
--------------

- `sample_data/animals_sample.csv` contains example rows you can import into MySQL or use as reference.
- `sample_data/README.md` explains how to map CSV columns to the database tables.
- The `uploads/` folder is where animal images are stored; place some example images here if you want to simulate records.


Notes on the CNN Model
----------------------

- `model/cnn_model.py` defines a small Convolutional Neural Network using TensorFlow/Keras.
- For this starter template, the network is **not pre-trained**. It is meant as a scaffold so you can:
  - Train on your own dataset of animal images.
  - Save the trained weights to disk.
  - Load the model and use it to predict species/breed or generate embeddings.

In production, you would:

- Prepare a dataset of labeled animal images (species, breed).
- Train the CNN offline (possibly in a notebook).
- Export the model to a `.h5` or SavedModel format.
- Modify `cnn_model.py` to load the trained model and call it in `app.py` during recognition.


Security and Production Considerations
-------------------------------------

This is a **starter** project and does not include:

- Authentication and authorization for NGO staff.
- Payment gateway integration for real donations.
- Robust error handling and logging.
- Rate limiting, CSRF protection, advanced validation, etc.

You should add these before using the system in a real NGO setting.

