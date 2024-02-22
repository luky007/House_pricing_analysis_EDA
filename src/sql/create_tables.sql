-- Create the tables in the db.
CREATE TABLE house_data (
  house_id INT PRIMARY KEY,
  n_bedroom INT,
  n_bathroom INT,
  n_stories INT,
  n_parking_slot INT,
  is_mainroad BOOLEAN,
  has_guestroom BOOLEAN,
  has_basement BOOLEAN,
  has_hot_water BOOLEAN,
  has_air_conditioning BOOLEAN,
  is_pref_area BOOLEAN,
  furnishing_id INT,
  INDEX idx_furnishing_id (furnishing_id)
);

CREATE TABLE furnishing_status (
  furnishing_id INT PRIMARY KEY,
  furnishing_status VARCHAR(50),
  CHECK (furnishing_id BETWEEN 0 AND 2),
  FOREIGN KEY (furnishing_id) REFERENCES house_data (furnishing_id)
);


CREATE TABLE house_price_data (
  house_id INT PRIMARY KEY,
  price INT,
  area INT,
  FOREIGN KEY (house_id) REFERENCES house_data (house_id)
);
