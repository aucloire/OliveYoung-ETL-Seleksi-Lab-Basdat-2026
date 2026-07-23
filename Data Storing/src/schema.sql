CREATE USER oliveyoung_admin WITH PASSWORD 'seleksibasdat2026';
GRANT ALL PRIVILEGES ON DATABASE oliveyoung_db TO oliveyoung_admin;
GRANT ALL ON SCHEMA public TO oliveyoung_admin;

CREATE TABLE Categories (
    category_id UUID PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Skin_Concerns (
    concern_id UUID PRIMARY KEY,
    concern_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Skin_Types (
    type_id UUID PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Products (
    product_id VARCHAR(50) PRIMARY KEY,
    clean_name VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    why_we_love_it TEXT,
    featured_ingredients_desc TEXT,
    how_to_use TEXT,
    batch_timestamp TIMESTAMP NOT NULL
);

CREATE TABLE Product_Category (
    product_id VARCHAR(50) REFERENCES Products(product_id) ON DELETE CASCADE ON UPDATE CASCADE,
    category_id UUID REFERENCES Categories(category_id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, category_id)
);

CREATE TABLE Product_Concern (
    product_id VARCHAR(50) REFERENCES Products(product_id) ON DELETE CASCADE ON UPDATE CASCADE,
    concern_id UUID REFERENCES Skin_Concerns(concern_id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, concern_id)
);

CREATE TABLE Product_Type (
    product_id VARCHAR(50) REFERENCES Products(product_id) ON DELETE CASCADE ON UPDATE CASCADE,
    type_id UUID REFERENCES Skin_Types(type_id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, type_id)
);

CREATE TABLE SKUs (
    sku_id UUID PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL REFERENCES Products(product_id) ON DELETE CASCADE ON UPDATE CASCADE,
    original_sku_name VARCHAR(250) NOT NULL,
    original_price NUMERIC(10,2) NOT NULL,
    sale_price NUMERIC(10,2) NOT NULL,
    discount_amount NUMERIC(5,2) -- Akan diisi otomatis oleh Trigger
);

CREATE TABLE Ingredients (
    ingredient_id UUID PRIMARY KEY,
    sku_id UUID NOT NULL REFERENCES SKUs(sku_id) ON DELETE CASCADE,
    liquid_variant VARCHAR(250),
    ingredient_name VARCHAR(250) NOT NULL
);

-- Function & Trigger untuk hitung persenan diskon
CREATE OR REPLACE FUNCTION calculate_discount()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.original_price > 0 AND NEW.original_price > NEW.sale_price THEN
        NEW.discount_amount := ROUND(((NEW.original_price - NEW.sale_price) / NEW.original_price) * 100, 2);
    ELSE
        NEW.discount_amount := 0;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calculate_discount
BEFORE INSERT OR UPDATE ON SKUs
FOR EACH ROW
EXECUTE FUNCTION calculate_discount();