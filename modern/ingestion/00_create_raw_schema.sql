CREATE SCHEMA IF NOT EXISTS modern_raw;

CREATE TABLE IF NOT EXISTS modern_raw.online_retail_raw (
    invoice TEXT,
    stock_code TEXT,
    description TEXT,
    quantity TEXT,
    invoice_date TEXT,
    price TEXT,
    customer_id TEXT,
    country TEXT
);

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'modern_raw';
