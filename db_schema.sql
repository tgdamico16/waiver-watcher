CREATE TABLE jobs (
  job_id UUID PRIMARY KEY,
  status VARCHAR(20) NOT NULL
);

CREATE TABLE player_projections (
  id INTEGER PRIMARY KEY,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  position VARCHAR(50),
  team VARCHAR(50),
  projected_points NUMERIC
);