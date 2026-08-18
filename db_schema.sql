CREATE TABLE jobs (
  job_id UUID PRIMARY KEY,
  status VARCHAR(20) NOT NULL
);

CREATE TABLE last_updated (
  position VARCHAR(50),
  week VARCHAR(50),
  season VARCHAR(50),
  updated_at TIMESTAMPTZ not null,

  PRIMARY KEY (position, week, season)
);

CREATE TABLE players (
  id INTEGER,
  position VARCHAR(50),
  week VARCHAR(50),
  season VARCHAR(50),
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  team VARCHAR(50),
  projected_points NUMERIC,

  PRIMARY KEY (id, position, week, season)
);