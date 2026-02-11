CREATE TABLE cars (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT,
    price_usd INT,
    odometer INT,
    username TEXT,
    phone_number VARCHAR(15),
    image_url TEXT,
    image_count INT,
    car_number TEXT,
    car_vin TEXT,
    datetime_found TIMESTAMP DEFAULT now()
)