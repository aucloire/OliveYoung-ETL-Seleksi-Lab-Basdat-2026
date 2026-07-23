/* 
    File ini menunjukkan contoh penggunaan oliveyoung_db untuk mendapatkan
    informasi. File ini juga dibuat untuk menerapkan spesifikasi BONUS pada
    Seleksi Basdat 2026, yaitu melakukan 3 query optimasi.
*/

-- INFORMASI 1: Analisis Produk Hypoallergenic
EXPLAIN ANALYZE
SELECT p.clean_name, p.brand, c.category_name, p.why_we_love_it
FROM Products AS p
JOIN Product_Category AS pc ON pc.product_id = p.product_id
JOIN Categories AS c ON c.category_id = pc.category_id
WHERE c.category_name = 'Cream' AND p.product_id NOT IN (
    SELECT DISTINCT p2.product_id 
    FROM Ingredients AS i
    JOIN SKUs AS s ON s.sku_id = i.sku_id
    JOIN Products AS p2 ON p2.product_id = s.product_id
    WHERE i.ingredient_name IN ('Fragrance', 'Alcohol')
);

-- indexing based on INFORMASI 1
CREATE INDEX idx_ingredients_name ON Ingredients(ingredient_name);
CREATE INDEX idx_ingredients_sku_id ON Ingredients(sku_id);
CREATE INDEX idx_skus_product_id ON SKUs(product_id);
CREATE INDEX idx_pc_category_id ON Product_Category(category_id);
CREATE INDEX idx_pc_product_id ON Product_Category(product_id);

-- INFORMASI 2: Mencari Skincare untuk Concern Blackheads, Well-aging, dan Visible Pores
-- before query tuning
EXPLAIN ANALYZE
SELECT p.clean_name, p.brand, s.original_sku_name, s.sale_price AS price
FROM SKUs AS s
JOIN Products AS p ON p.product_id = s.product_id
WHERE p.product_id IN (
    SELECT pc.product_id 
    FROM Product_Concern pc 
    JOIN Skin_Concerns sc ON sc.concern_id = pc.concern_id 
    WHERE sc.concern_name = 'Blackheads'
)
AND p.product_id IN (
    SELECT pc.product_id 
    FROM Product_Concern pc 
    JOIN Skin_Concerns sc ON sc.concern_id = pc.concern_id 
    WHERE sc.concern_name = 'Visible Pores'
)
AND p.product_id IN (
    SELECT pc.product_id 
    FROM Product_Concern pc 
    JOIN Skin_Concerns sc ON sc.concern_id = pc.concern_id 
    WHERE sc.concern_name = 'Well-aging'
);
-- after query tuning
EXPLAIN ANALYZE
SELECT p.clean_name, p.brand, s.original_sku_name, s.sale_price AS price
FROM SKUs AS s
JOIN Products AS p ON p.product_id = s.product_id
JOIN Product_Concern AS pc ON pc.product_id = p.product_id
JOIN Skin_Concerns AS sc ON sc.concern_id = pc.concern_id
WHERE sc.concern_name IN ('Blackheads', 'Visible Pores', 'Well-aging')
GROUP BY p.clean_name, p.brand, s.original_sku_name, s.sale_price
HAVING COUNT(DISTINCT sc.concern_id) = 3;

-- INFORMASI 3: Analisis Ingredients Populer untuk Well-aging Essence & Serum
-- before query tuning
EXPLAIN ANALYZE
SELECT i.ingredient_name, COUNT(i.ingredient_name) AS total_used
FROM Ingredients AS i
JOIN SKUs AS s ON s.sku_id = i.sku_id
JOIN Product_Category AS pca ON pca.product_id = s.product_id 
    AND pca.category_id = (SELECT category_id FROM Categories WHERE category_name = 'Essence & Serum')
JOIN Product_Concern AS pco ON pco.product_id = s.product_id
    AND pco.concern_id = (SELECT concern_id FROM Skin_Concerns WHERE concern_name = 'Well-aging')
WHERE i.ingredient_name NOT IN (
    'Water', 'Purified Water', 'Glycerin', 'Butylene Glycol', 
    '1,2-Hexanediol', 'Dipropylene Glycol', 'Propanediol', 
    'Disodium EDTA', 'Caprylyl Glycol', 'Ethylhexylglycerin'
)
GROUP BY i.ingredient_name
HAVING COUNT(i.ingredient_name) >= 3
ORDER BY total_used DESC;

-- indexing
DROP INDEX idx_ingredients_sku_id;
DROP INDEX idx_skus_product_id;
CREATE INDEX idx_ingredients_sku_id ON Ingredients (sku_id, ingredient_name);
CREATE INDEX idx_skus_product_id ON SKUs (product_id, sku_id);

-- after query tuning
EXPLAIN ANALYZE
SELECT i.ingredient_name, COUNT(i.ingredient_name) AS total_used
FROM Ingredients AS i
JOIN SKUs AS s ON s.sku_id = i.sku_id
JOIN Product_Category AS pca ON pca.product_id = s.product_id 
JOIN Categories AS c ON c.category_id = pca.category_id
JOIN Product_Concern AS pco ON pco.product_id = s.product_id
JOIN Skin_Concerns AS sc ON sc.concern_id = pco.concern_id
WHERE c.category_name = 'Essence & Serum' 
    AND sc.concern_name = 'Well-aging'
    AND i.ingredient_name NOT IN (
        'Water', 'Purified Water', 'Glycerin', 'Butylene Glycol', 
        '1,2-Hexanediol', 'Dipropylene Glycol', 'Propanediol', 
        'Disodium EDTA', 'Caprylyl Glycol', 'Ethylhexylglycerin'
  )
GROUP BY i.ingredient_name
HAVING COUNT(i.ingredient_name) >= 3
ORDER BY total_used DESC;