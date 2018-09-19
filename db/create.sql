CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY,
    device_id INTEGER NOT NULL,
    --    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    action TEXT,
    value REAL,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id INTEGER PRIMARY KEY,
    device_id INTEGER NOT NULL,
    --    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    value REAL NOT NULL,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY,
    provider_name TEXT NOT NULL, 
    provider TEXT,
    units TEXT,
    display_name TEXT,
    description TEXT,
    calibration TEXT -- comma separated polynomial, x0,x1,x2
);
