CREATE SCHEMA IF NOT EXISTS traditional_dw;

CREATE TABLE IF NOT EXISTS traditional_dw.dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_id NUMERIC UNIQUE
);

CREATE TABLE IF NOT EXISTS traditional_dw.dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    stock_code TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS traditional_dw.dim_date (
    date_key BIGSERIAL PRIMARY KEY,
    full_timestamp TIMESTAMP NOT NULL UNIQUE,
    calendar_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    hour INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS traditional_dw.dim_country (
    country_key BIGSERIAL PRIMARY KEY,
    country_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS traditional_dw.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,

    invoice_no TEXT NOT NULL,

    customer_key BIGINT,
    product_key BIGINT NOT NULL,
    date_key BIGINT NOT NULL,
    country_key BIGINT NOT NULL,

    quantity NUMERIC NOT NULL,
    unit_price NUMERIC NOT NULL,
    sales_amount NUMERIC NOT NULL,

    is_cancellation BOOLEAN NOT NULL,

    missing_customer_flag BOOLEAN NOT NULL DEFAULT FALSE,
    missing_description_flag BOOLEAN NOT NULL DEFAULT FALSE,

    source_row BIGINT,

    CONSTRAINT fk_fact_customer
        FOREIGN KEY (customer_key)
        REFERENCES traditional_dw.dim_customer(customer_key),

    CONSTRAINT fk_fact_product
        FOREIGN KEY (product_key)
        REFERENCES traditional_dw.dim_product(product_key),

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_key)
        REFERENCES traditional_dw.dim_date(date_key),

    CONSTRAINT fk_fact_country
        FOREIGN KEY (country_key)
        REFERENCES traditional_dw.dim_country(country_key)
);