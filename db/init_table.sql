CREATE TABLE cars (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    price_usd INT NOT NULL,
    odometer INT NOT NULL,
    username TEXT NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    image_url TEXT NOT NULL,
    image_count INT NOT NULL,
    car_number TEXT,
    car_vin TEXT,
    datetime_found TIMESTAMP DEFAULT now()
)