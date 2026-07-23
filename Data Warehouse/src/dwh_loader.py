'''
    Olive Young Global - Data Warehouse Loader
    Script dwh_loader.py ini melakukan proses ETL (Extract, Transform, Load) 
    dari database operasional (OLTP) ke dalam arsitektur Data Warehouse (Star Schema).
'''

import os
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv

class OliveYoungDWHLoader:
    def __init__(self):
        load_dotenv()
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_pass = os.getenv("DB_PASS")

    def _get_connection(self):
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_pass
        )

    def extract_and_transform(self, cursor):
        print("⚙️ Mengekstraksi dan Mentransformasi data dari OLTP...")
        
        query = """
        WITH prod_categories AS (
            SELECT pc.product_id, COUNT(pc.category_id) as cat_cnt, STRING_AGG(c.category_name, ', ') as cat_list
            FROM Product_Category pc JOIN Categories c ON pc.category_id = c.category_id GROUP BY pc.product_id
        ),
        prod_concerns AS (
            SELECT pc.product_id, COUNT(pc.concern_id) as conc_cnt, STRING_AGG(sc.concern_name, ', ') as conc_list
            FROM Product_Concern pc JOIN Skin_Concerns sc ON pc.concern_id = sc.concern_id GROUP BY pc.product_id
        ),
        prod_types AS (
            SELECT pt.product_id, COUNT(pt.type_id) as type_cnt, STRING_AGG(st.type_name, ', ') as type_list
            FROM Product_Type pt JOIN Skin_Types st ON pt.type_id = st.type_id GROUP BY pt.product_id
        ),
        sku_ingredients AS (
            SELECT sku_id, COUNT(ingredient_id) as ing_cnt
            FROM Ingredients GROUP BY sku_id
        )
        SELECT 
            s.sku_id, p.product_id, p.clean_name, p.brand, p.batch_timestamp,
            s.original_price, s.sale_price, s.discount_amount,
            COALESCE(si.ing_cnt, 0) as ingredient_count,
            COALESCE(cat.cat_cnt, 0) as category_count, cat.cat_list,
            COALESCE(con.conc_cnt, 0) as concern_count, con.conc_list,
            COALESCE(typ.type_cnt, 0) as type_count, typ.type_list
        FROM SKUs s
        JOIN Products p ON s.product_id = p.product_id
        LEFT JOIN Sku_Ingredients si ON s.sku_id = si.sku_id
        LEFT JOIN Prod_Categories cat ON p.product_id = cat.product_id
        LEFT JOIN Prod_Concerns con ON p.product_id = con.product_id
        LEFT JOIN Prod_Types typ ON p.product_id = typ.product_id;
        """
        cursor.execute(query)
        return cursor.fetchall()

    def load_to_dw(self, cursor, data):
        print(f"-> Memuat {len(data)} baris ke Data Warehouse (Star Schema)...")
        
        dim_date_data, dim_product_data, fact_data = [], [], []
        processed_dates, processed_products = set(), set()

        for row in data:
            (sku_id, product_id, clean_name, brand, batch_ts, orig_price, sale_price, 
             disc_amt, ing_cnt, cat_cnt, cat_list, conc_cnt, conc_list, typ_cnt, typ_list) = row

            date_id = int(batch_ts.strftime('%Y%m%d'))
            if date_id not in processed_dates:
                dim_date_data.append((date_id, batch_ts.date(), batch_ts.year, (batch_ts.month-1)//3 + 1, batch_ts.month, batch_ts.day))
                processed_dates.add(date_id)

            if product_id not in processed_products:
                dim_product_data.append((product_id, clean_name, brand, cat_list, conc_list, typ_list))
                processed_products.add(product_id)

            fact_data.append((sku_id, product_id, date_id, orig_price, sale_price, disc_amt, ing_cnt, cat_cnt, conc_cnt, typ_cnt))

        extras.execute_values(cursor, 
            "INSERT INTO dwh.dim_date (date_id, full_date, year, quarter, month, day) VALUES %s ON CONFLICT (date_id) DO NOTHING", 
            dim_date_data)
            
        extras.execute_values(cursor, 
            "INSERT INTO dwh.dim_product (product_id, clean_name, brand, category_list, skin_concern_list, skin_type_list) VALUES %s ON CONFLICT (product_id) DO NOTHING", 
            dim_product_data)
            
        extras.execute_values(cursor, 
            """INSERT INTO dwh.fact_sku_metrics 
               (sku_id, product_id, date_id, original_price, sale_price, discount_amount, ingredient_count, category_count, concern_count, type_count) 
               VALUES %s""", 
            fact_data)

        print("[+] Bulk insert ke Data Warehouse berhasil.")

    def run(self):
        print("🚀 Memulai proses pemindahan data (ETL) ke Data Warehouse...")
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            olap_data = self.extract_and_transform(cur)
            
            if olap_data:
                self.load_to_dw(cur, olap_data)
                conn.commit()
                print("\n✓ DONE: Seluruh data berhasil dipindahkan ke skema Data Warehouse.")
            else:
                print("\n[-] Tidak ada data dari OLTP untuk diekstrak.")
                
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"\n✕ ERROR: Transaksi dibatalkan. {e}")
        finally:
            if conn:
                cur.close()
                conn.close()
                print("-> Koneksi database telah ditutup.")

if __name__ == "__main__":
    dwh_loader = OliveYoungDWHLoader()
    dwh_loader.run()