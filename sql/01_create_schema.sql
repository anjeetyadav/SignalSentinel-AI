-- SignalSentinel AI
-- Purpose: Create the core database tables.

CREATE TABLE IF NOT EXISTS calendar (
d VARCHAR(10) PRIMARY KEY,
date DATE NOT NULL UNIQUE,
wm_yr_wk INTEGER NOT NULL,
weekday VARCHAR(20),
wday INTEGER,
month INTEGER,
year INTEGER,
event_name_1 VARCHAR(100),
event_type_1 VARCHAR(50),
event_name_2 VARCHAR(100),
event_type_2 VARCHAR(50),
snap_CA INTEGER,
snap_TX INTEGER,
snap_WI INTEGER
);

CREATE TABLE IF NOT EXISTS sell_prices (
store_id VARCHAR(10) NOT NULL,
item_id VARCHAR(20) NOT NULL,
wm_yr_wk INTEGER NOT NULL,
sell_price NUMERIC(12, 4) NOT NULL,
PRIMARY KEY (store_id, item_id, wm_yr_wk)
);

CREATE TABLE IF NOT EXISTS sales (
id VARCHAR(100) NOT NULL,
item_id VARCHAR(20) NOT NULL,
dept_id VARCHAR(20) NOT NULL,
cat_id VARCHAR(20) NOT NULL,
store_id VARCHAR(10) NOT NULL,
state_id VARCHAR(10) NOT NULL,
d VARCHAR(10) NOT NULL,
units_sold INTEGER NOT NULL CHECK (units_sold >= 0),
PRIMARY KEY (id, d)
);
