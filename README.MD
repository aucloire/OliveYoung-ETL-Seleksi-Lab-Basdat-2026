<h1 align="center">
  <br>
  Olive Young Global Web Scraping Project
  <br>
  <br>
</h1>

<h2 align="left">
  <br>
  Author
  <br>
</h2>
Name: Ellaine Juvina <br>
NIM : 18224071
  <br>

## Deskripsi Singkat
Olive Young adalah ritel kosmetik, kesehatan, dan kecantikan nomor 1 di Korea Selatan. Kini, Olive Young telah tersedia di e-commerce internasional, yaitu [Olive Young Global](https://global.oliveyoung.com).

Berdasarkan *website* tersebut, didapatkan sejumlah data yang berkaitan dengan produk-produk *skincare* yang dijual di *e-commerce* tersebut, seperti produk, *brand*, harga, deskripsi, dan komposisi.

*Website* Olive Young Global dipilih dalam proyek ETL ini karena ketertarikan author terhadap *K-Beauty*, terutama *skincare*. Data-data yang diperoleh dari Olive Young Gloval dapat memberikan informasi tambahan terkait komposisi yang umumnya digunakan untuk suatu kondisi kulit pada kategori *skincare* tertentu.

*Project* ini dibatasi agar tidak melakukan scraping terhadap seluruh katalog pada Olive Young Global. *Scraping* dilakukan dengan *filtering* untuk mendapatkan produk sesuai dengan kategorinya.
- **Skincare Category**: Moisturizers (Toner, Essence & Serum, Cream), Cleansers (Cleansing Foams)
- **Skin Concern**: Acne, Blackheads, Brightening, Moisturising, Soothing, Visible Pores, Well-aging
- **Skin Types**: Combination&Normal, Dry, Oily, Sensitive

Selain itu, *scraper* dibatasi pada maksimal 72 produk untuk setiap filter.

<br>

## Cara Menggunakan Scraper
### Prasyarat
- Python 3.12 telah terinstal di sistem.
- RDBMS PostgreSQL telah terinstal dan berjalan. Buat sebuah *database* baru dengan nama oliveyoung_db dan jalankan *script* DDL yang berada di `Data Storing/src/schema.sql`.
- *Library* Python yang dibutuhkan telah terinstal. Instalasi dapat dilakukan dengan *run command* `pip install -r requirements.txt`
- Buat sebuah file `.env` di *root* untuk menyimpan kredensial *database* dengan isi sebagai berikut:
```env
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=nama_database_kamu
    DB_USER=username_postgres_kamu
    DB_PASS=password_postgres_kamu
```

### Langkah Eksekusi
1. Lakukan *clone* terhadap repositori ini dengan command:
```
    git clone https://github.com/aucloire/OliveYoung-ETL-Seleksi-Lab-Basdat-2026.git
```
2. Buka terminal dan arahkan *directory* ke dalam folder `Data Scraping/src`.
3. Jalankan *script scraper* dengan *command*: 
```
    python scraper.py
```
4. Tunggu hingga proses *scraping* selesai. *Script* akan otomatis melakukan *preprocessing* dan memecah data ke beberapa JSON.
5. Untuk memasukkan data ke dalam *database*, jalankan *script* `loader.py` pada folder `Data Storing/src`.

### Output
Hasil dari proses *scraping* yaitu 9 *file* JSON yang terpisah berdasarkan entitasnya. Seluruh *file* JSON ini akan secara otomatis tersimpan di dalam *directory* `Data Scraping/data`.

<br>

## Struktur Data JSON
- `products.json`
```
    {
        "product_id": "GA240121573",
        "clean_name": "AESTURA Atobarrier 365 Cream",
        "brand": "AESTURA",
        "why_we_love_it": "Enhanced barrier hydration with high-density ceramides specialized for sensitive skin. It is an evolved product with high-density ceramides specialized for sensitive skin. Sensitive skin requires long and dense high-density ceramides.",
        "featured_ingredients_desc": "It is a product that contains second-generation moisturizing capsules fortified with high-density ceramides. Through 40 years of painstaking research on sensitive skin, we have thoroughly verified the length, type, absorption, and retention of ceramides to create a denser moisturizing capsule. We upgraded the short and inadequate ceramides of sensitive skin to a denser and more robust structure and included long-chain ceramides and linker ceramides that connect them. Artificial fragrance-free, synthetic colorant-free, 9 FREE products.",
        "how_to_use": "After cleansing in the morning and evening, apply an appropriate amount evenly to the skin and absorb."
    }
```
- `skus.json`
```
    {
        "sku_id": "019f8a17-5440-70d9-88f0-c8ec9c022cd6",
        "product_id": "GA250127893",
        "original_sku_name": "SKIN1004 Madagascar Centella Ampoule 100ml",
        "original_price": 22.0,
        "sale_price": 18.7
    }
```
- `ingredients.json` 
```
    {
        "ingredient_id": "019f89ad-c79b-7947-8084-dec0828e4c8b",
        "sku_id": "019f89ad-baa4-724d-93ee-b9e345427d2d",
        "liquid_variant": "Fresh Green Cleanser",
        "ingredient_name": "Camellia Sinensis Leaf Powder"
    }
```
- `categories.json`
```
    {
        "category_id": "019f89a3-e372-7f12-8796-9c4eae1e650d",
        "category_name": "Toner"
    }
```
- `skin_concerns.json`
```
    {
        "concern_id": "019f89a3-e379-7461-a812-0dbbd2b9ca12",
        "concern_name": "Moisturising"
    }
```
- `skin_types.json` 
```
    {
        "type_id": "019f89a3-e37d-7d41-960d-3da1f4feb20b",
        "type_name": "Combination&Normal"
    }
```
- `product_category.json`
```
    {
        "product_id": "GA230819791",
        "category_id": "019f89a3-e372-7f12-8796-9c4eae1e650d"
    }
```
- `product_concern.json` 
```
    {
        "product_id": "GA240724586",
        "concern_id": "019f89a3-e376-751d-930d-90d2e699071a"
    }
```
- `product_type.json`
```
    {
        "product_id": "GA250127641",
        "type_id": "019f89a3-e37d-7d41-960d-3da1f4feb20b"
    }
```

<br>

## Desain Database (ERD & Relasional)
Desain di bawah menggunakan *tools* dari [draw.io](draw.io). 

1. ***Entity-Relationship Diagram* (ERD)**
![ERD](<Data Storing/design/ERD.png>)

2. **Diagram Relasional**
![Relasional Diagram](<Data Storing/design/Relasional Diagram.png>)

<br>

## Proses Translasi ERD ke Diagram Relasional
1. **One-to-Many:**
  Hubungan *one-to-many* (1:M) antara SKUs-Ingredients dan Products-SKUs akan menghasilkan *foreign key* yang tersimpan di entitas dengan *cardinality **many*** yang me-*reference* ke entitas dengan *cardinality **one***.

2. **Many-to-Many:**
  Hubungan *many-to-many* (M:N) antara Products dengan Categories, Skin_Concerns, dan Skin_Types akan menghasilkan sebuah relasi baru yang menyimpan *primary key* dari kedua entitas terkait sebagai *foreign key* untuk dijadikan juga *composite primary key* pada relasi baru tersebut.

3. **Foreign Key References:**
   - Ingredients(sku_id) -> SKUs(sku_id)
   - SKUs(product_id) -> Products(product_id)
   - Product_Category(product_id) -> Products(product_id)
   - Product_Concern(product_id) -> Products(product_id)
   - Product_Type(product_id) -> Products(product_id)
   - Product_Category(category_id) -> Categories(category_id)
   - Product_Concern(concern_id) -> Skin_Concerns(concern_id)
   - Product_Type(type_id) -> Skin_Types(type_id)

<br>

## Screenshots Eksekusi Program
- `products`
![products](<Data Storing/screenshot/products.png>)

- `skus`
![skus](<Data Storing/screenshot/skus.png>)

- `ingredients` 
![ingredients](<Data Storing/screenshot/ingredients.png>)

- `categories`
![categories](<Data Storing/screenshot/categories.png>)

- `skin_concerns`
![skin_concerns](<Data Storing/screenshot/skin_concerns.png>)

- `skin_types` 
![skin_types](<Data Storing/screenshot/skin_types.png>)

- `product_category`
![product_category](<Data Storing/screenshot/product_category.png>)

- `product_concern` 
![product_concern](<Data Storing/screenshot/product_concern.png>)

- `product_type`
![product_type](<Data Storing/screenshot/product_type.png>)

> Eksekusi Program untuk Bonus Data Warehouse
- `dim_product`
![dim_product](<Data Warehouse/screenshot/dwh-dim_product.png>)

- `dim_date`
![dim_date](<Data Warehouse/screenshot/dwh-dim_date.png>)

- `fact_sku_metrics`
![fact_sku_metrics](<Data Warehouse/screenshot/dwh-fact_sku_metrics.png>)

<br>

## Dokumentasi Bonus
### Bonus 1: Data Warehouse
Arsitektur *Data Warehouse* (OLAP) dirancang dengan ***Star Schema***. Pendekatan ini dipilih untuk mengurangi operasi `JOIN` yang kompleks saat melakukan *query* analitik, sehingga performa pembacaan data menjadi jauh lebih efisien.

Tabel dengan relasi *many-to-many* dari oliveyoung_db, seperti Categories, Skin_Concerns, dan Skin_Types, didenormalisasi menjadi teks gabungan di tabel dimensi, dan diagregrasi menjadi nilai *count* di *fact table*.

#### Komponen Star Schema
1. ***Fact Table* (`fact_sku_metrics`)** menyimpan nilai kuantitatif hasil transaksi/ekstraksi, seperti harga, persenan diskon, banyak komposisi dalam produk, dan jumlah kategori/masalah/tipe kulit.
2. ***Dimension Table***
   - `dim_product` menyimpan atribut yang bersifat deskriptif dari suatu produk, seperti brand, nama produk, dll.
   - `dim_date` menyimpan atribut tanggal yang diesktrak dari `batch_timestamp` untuk analisis yang bersifat *time-series*.

#### Desain ERD & Star Schema Data Warehouse
1. ERD Data Warehouse
![ERD DWH](<Data Warehouse/design/dwh_ERD.png>)

2. Diagram Relasional (Star Schema) Data Warehouse
![Star Schema](<Data Warehouse/design/Star Schema.png>)

#### Query Analitik
1. Analisis Masalah Kulit dengan Harga Produk Skincare
```
    WITH unnested_concerns AS (
        SELECT 
            TRIM(UNNEST(string_to_array(dp.skin_concern_list, ','))) AS individual_skin_concern,
            f.sale_price,
            f.discount_amount
        FROM dwh.fact_sku_metrics AS f
        JOIN dwh.dim_product AS dp ON f.product_id = dp.product_id
        WHERE dp.skin_concern_list IS NOT NULL
    )
    SELECT 
        individual_skin_concern,
        COUNT(*) AS product_count,
        ROUND(AVG(sale_price), 2) AS average_sale_price,
        ROUND(AVG(discount_amount), 2) AS average_discount
    FROM unnested_concerns
    GROUP BY individual_skin_concern
    HAVING AVG(discount_amount) > 15
    ORDER BY average_sale_price DESC
    LIMIT 3;
```
![Hasil Query 1](<Data Warehouse/screenshot/query-analitik-1.png>)

2. Analisis Brand vs Diskon
```
    SELECT 
        dp.brand,
        COUNT(f.sku_id) AS total_skus,
        ROUND(AVG(f.discount_amount), 2) AS avg_brand_discount,
        ROUND(AVG(f.ingredient_count), 0) AS avg_ingredients,
        ROUND(AVG(f.discount_amount) - AVG(AVG(f.discount_amount)) OVER (), 2) AS discount_diff_from_market,
        RANK() OVER (ORDER BY AVG(f.discount_amount) DESC) AS discount_strategy_rank
    FROM dwh.fact_sku_metrics AS f
    JOIN dwh.dim_product AS dp ON f.product_id = dp.product_id
    GROUP BY dp.brand
    HAVING COUNT(f.sku_id) > 5
    ORDER BY discount_strategy_rank;
```
![Hasil Query 2](<Data Warehouse/screenshot/query-analitik-2.png>)

### Bonus 2: Automated Scheduling
*Automated scheduling* diimpplementasikan menggunakan OS Scheduler, seperti Task Scheduler pada Windows, yang menjalankan *wrapper script* `run_etl.bat` setiap hari pada jam tertentu. Sistem ini mengamankan *idempotency* menggunakan klausa ON CONFLICT pada metode `_bulk_insert()` di PostgreSQL untuk memastikan tidak ada redundansi data. Perbedaan antarsiklus dapat dilihat dari kolom `batch_timestamp` di tabel `Products`
```
oliveyoung_db=# select product_id, clean_name, brand, batch_timestamp from products order by batch_timestamp desc limit 5;
```
| product_id | clean_name | brand | batch_timestamp |
| :--- | :--- | :--- | :--- |
| GA230217695 | AMPLE:N Ceramide Shot Ampoule | AMPLE:N | 2026-07-23 17:33:31 |
| GA260439734 | Anua PDRN Hyaluronic Capsule 100 Serum | Anua | 2026-07-23 17:33:09 |
| GA260338900 | ROUND LAB Sensitive Skin Calming Routine | ROUND LAB | 2026-07-23 17:32:47 |
| GA260136963 |  makeprem Inteca For Men Soothing All-In-One | makeprem | 2026-07-23 12:36:05 |
| GA250832687 | Arencia Holy Hyssop Serum 30 | Arencia | 2026-07-23 12:36:05 |
> Automated scheduling dicoba dengan melakukan pembatasan terhadap scraping ke 3 produk untuk mempercepat proses testing dan menunjukkan perbedaan di database.

Setiap kali *scheduler* berjalan, sistem secara otomatis membuat *file log* berbasis *timestamp* yang bisa dilihat di *directory* `logs/` dengan format `etl_pipeline_YYYYMMDD_HHMMSS.log`. *File* tersebut merekam seluruh proses ETL *pipeline*, mulai dari *scraping*, pemuatan data OLTP, hingga pembaruan *Data Warehouse* (OLAP) untuk memudahkan proses *debugging* dan audit.

### Bonus 3: Optimasi Query
Bonus ini dikerjakan dengan terlebih dahulu menentukan 3 informasi yang ingin didapatkan dari `oliveyoung_db`. Selanjutnya, dilakukan `EXPLAIN ANALYZE` terhadap query yang dihasilkan untuk kemudian menganalisis hal-hal yang perlu dioptimasi.

#### 1. Informasi 1: Analisis Produk Hypoallergenic
Query ini bertujuan untuk mencari daftar nama skincare kategori **Cream** yang hypoallergenic dengan memastikan bahwa skincare tersebut bebas dari komposisi pemicu iritasi, biasanya *fragrance* atau *alcohol*.

Sebelum:
![Sebelum](<Query Optimasi/screenshot/informasi1-explainanalyze-before.png>)

**Strategi Optimasi:** Penerapan B-Tree Indexing pada relasi yang terlibat, seperti Ingredients, SKUs, dan Product_Category untuk menghilangkan sequential scan, sehingga menurunkan execution time.

Sesudah:
![Sesudah](<Query Optimasi/screenshot/informasi1-explainanalyze-after.png>)

#### 2. Informasi 2: Analisis Produk untuk 3 Skin Concern Spesifik
Query ini bertujuan untuk mencari produk yang mampu menangani 3 masalah kulit sekaligus, misalnya **Blackheads, Visible Pores, dan Well-aging**. Selain itu, query ini juga akan menampilkan harga jualnya.

Sebelum: 
![sebelum](<Query Optimasi/screenshot/informasi2-explainanalyze-before.png>)

**Strategi Optimasi:** Melakukan query tuning untuk menghilangkan multiple subqueries menggunakan metode HAVING COUNT sehingga database engine hanya perlu melakukan 1 kali hash join.

Sesudah:
![sesudah](<Query Optimasi/screenshot/informasi2-explainanalyze-after.png>)

#### 3. Informasi 3: Analisis Komposisi Populer
Query ini bertujuan untuk menganalisis bahan kimia yang paling sering digunakan pada skincare **Essence & Serum** yang menargetkan masalah kulit **Well-aging** dengan menghilangkan base ingredients dari daftar.

Sebelum:
![sebelum](<Query Optimasi/screenshot/informasi3-explainanalyze-before.png>)

**Strategi Optimasi:** Menggunakan composite index untuk menurunkan total cost melalui index only scan.

Sesudah:
![sesudah](<Query Optimasi/screenshot/informasi3-explainanalyze-after.png>)

<br>

## Transparansi Penggunaan AI
1. **Bagian yang dibantu AI:** 
   - Pengerjaan Step 1 Data Scraping, yaitu *algorithm refinement* untuk menyederhanakan *script* dan *bug solving*. 
   - Pengerjaan Step 2 Data Storing, yaitu pembuatan `loader.py`
   - Pengerjaan Bonus 1 Data Warehouse, yaitu perencanaan data warehouse dan pembuatan `dwh_loader.py`
   - Pengerjaan Bonus 2 Automated Scheduling, yaitu pembuatan `run_etl.bat` dan `run_etl.sh`, serta *step-by-step* dalam mengerjakan bonus.
   
2. **Bagian yang dikerjakan sendiri:**
   - Pengerjaan Step 1 Data Scraping, yaitu penentuan topik dan *data source*, penentuan *library/framework* yang digunakan, data yang diambil, *inspect website* untuk mengambil *endpoint/xpath list* untuk dipakai di `scraper.py`, dan penentuan *preprocessing* yang harus dilakukan.
   - Pengerjaan Step 2 Data Modelling dan Data Storing, yaitu memodelkan ERD, Diagram Relasional, pembuatan `Data Storing/src/schema.sql` untuk RDBMS, dan implementasi *constraints* (*primary key, foreign key, trigger, dll.*).
   - Pengerjaan Bonus 1 Data Warehouse, yaitu penentuan data numerik yang ingin diambil, query analitik, perancangan ERD dan translasi ke relasional, pembuatan asumsi ERD
   - Pengerjaan Bonus 3 Query Optimasi

3. **Refleksi dari penggunaan AI:** 
   Penggunaan AI sangat membantu dalam mempercepat penyelesaian tugas dan *solving* masalah teknis, seperti melakukan *debugging* dan menyederhanakan logika kode. Namun, saya menyadari bahwa AI bertindak hanya sebagai sebuah asisten. Fondasi pemahaman terkait *database modelling*, penyusunan arsitektur, serta alur logika ekstraksi data tetap harus berasal ddari pemikiran *author* sendiri agar sistem yang dibangun terstruktur dengan benar dan dapat dipertanggungjawabkan. Melalui project ini, author kembali sadar bahwa setiap keputusan bukan dibuat oleh AI, melainkan oleh manusia.

<br>

## Referensi
**Sumber Data:** [Olive Young Global](https://global.oliveyoung.com)

**Library/Tools:**<br>
[Python 3.12.13 Documentation](https://docs.python.org/id/3.12/index.html)<br>
[PostgreSQL 18 Documentation](https://www.postgresql.org/docs/18/index.html)<br>
[Selenium with Python Documentation](https://selenium-python.readthedocs.io/)<br>
[Psycopg 2 Documentation](https://www.psycopg.org/docs/)<br>
[uuid6 Documentation](https://pypi.org/project/uuid6/)

**Tutorials:**<br>
[Use Cases of XPath Python In Selenium With Examples](https://www.testmuai.com/blog/python-xpath/)<br>
[Automating an ETL Pipeline with Windows Task Scheduler](https://innerjoin.bit.io/automating-an-etl-pipeline-with-windows-task-scheduler-ef069c63fc35?sharedUserId=ellainejh)<br>