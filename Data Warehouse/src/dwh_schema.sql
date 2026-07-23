CREATE SCHEMA IF NOT EXISTS dwh;
GRANT ALL ON SCHEMA dwh TO oliveyoung_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dwh TO oliveyoung_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA dwh TO oliveyoung_admin;

-- DIMENSION TABLE
CREATE TABLE dwh.dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT,
    quarter INT,
    month INT,
    day INT
);

CREATE TABLE dwh.dim_product (
    product_id VARCHAR(50) PRIMARY KEY,
    clean_name VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    category_list TEXT,
    skin_concern_list TEXT,
    skin_type_list TEXT
);

-- FACT TABLE
CREATE TABLE dwh.fact_sku_metrics (
    fact_id SERIAL PRIMARY KEY,
    sku_id UUID NOT NULL,
    product_id VARCHAR(50) REFERENCES dwh.dim_product(product_id),
    date_id INT REFERENCES dwh.dim_date(date_id),
    original_price NUMERIC(10,2),
    sale_price NUMERIC(10,2),
    discount_amount NUMERIC(5,2),    
    ingredient_count INT,
    category_count INT,
    concern_count INT,
    type_count INT
);