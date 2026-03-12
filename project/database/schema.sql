-- MySQL schema for Integrated NGO Platform for Animal Rescue, Identification,
-- Virtual Adoption and Donation.

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role ENUM('ngo_admin', 'donor') DEFAULT 'ngo_admin',
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS animals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id VARCHAR(64) NOT NULL UNIQUE,
    species VARCHAR(100),
    breed VARCHAR(150),
    rescue_date DATE,
    shelter_location VARCHAR(255),
    health_status VARCHAR(255),
    image_filename VARCHAR(255),
    image_hash CHAR(64),
    adoption_status ENUM('available', 'adopted', 'not_available') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS medical_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id INT NOT NULL,
    record_date DATE NOT NULL,
    description TEXT,
    treatment TEXT,
    vet_name VARCHAR(255),
    FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS adopters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS adoption_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id INT NOT NULL,
    adopter_id INT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT,
    FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE,
    FOREIGN KEY (adopter_id) REFERENCES adopters(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(255) NOT NULL,
    donor_email VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

