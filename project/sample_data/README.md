Sample Data for Integrated NGO Platform
=======================================

This folder contains simple starter data you can use while experimenting
with the application.


animals_sample.csv
------------------

Columns map directly to the `animals` table:

- `animal_id` – external identifier (e.g., tag or internal code)
- `species` – species of the animal (Dog, Cat, etc.)
- `breed` – breed, if known
- `rescue_date` – ISO date of rescue (YYYY-MM-DD)
- `shelter_location` – shelter or rescue location string
- `health_status` – free-text health status
- `adoption_status` – `available`, `adopted`, or `not_available`


Importing via MySQL
-------------------

One quick way to import is to open MySQL and run a `LOAD DATA` statement
after placing this CSV somewhere accessible to the MySQL server:

```sql
LOAD DATA LOCAL INFILE 'C:/path/to/animals_sample.csv'
INTO TABLE animals
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(animal_id, species, breed, rescue_date, shelter_location, health_status, adoption_status);
```

Alternatively, you can open the CSV in a GUI like MySQL Workbench and
use its import wizard to load rows into the `animals` table.

