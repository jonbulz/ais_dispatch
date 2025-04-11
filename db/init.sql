CREATE TABLE IF NOT EXISTS config (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS data (
    id SERIAL PRIMARY KEY,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    service TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    info TEXT
);

INSERT INTO config (key, value) VALUES
('active', ''),
('data_sent', '0'),
('data_max', '0'),
('interval', '1');
