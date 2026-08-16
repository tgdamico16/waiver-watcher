CREATE TABLE temperature (
  id SERIAL PRIMARY KEY,
  recorded_at TIMESTAMP NOT NULL,
  temperature DECIMAL(5,2) NOT NULL
);
