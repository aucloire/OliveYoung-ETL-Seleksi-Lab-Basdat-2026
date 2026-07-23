'''
    Olive Young Global - Data Loader
    Script loader.py ini memuat data dari file JSON hasil Scraping
    ke dalam PostgreSQL menggunakan metode bulk insert.
'''

import os
import json
import psycopg2
import datetime
import sys
from psycopg2 import extras
from dotenv import load_dotenv

class OliveYoungDBDataLoader:
    def __init__(self):
        load_dotenv()
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_pass = os.getenv("DB_PASS")
        
        self.base_data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Data Scraping', 'data')

    def _get_connection(self):
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_pass
        )

    def _load_json(self, filename: str) -> list:
        filepath = os.path.join(self.base_data_path, filename)
        if not os.path.exists(filepath):
            print(f"  [!] Peringatan: File {filename} tidak ditemukan.")
            return []
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _bulk_insert(self, cursor, table_name: str, columns: list, data: list, conflict_targets: list, do_update: bool = True):
        if not data:
            print(f"[-] Melewati {table_name}: Tidak ada data.")
            return
        
        col_names = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        conflict_target_str = ", ".join(conflict_targets)
        
        if do_update:
            update_cols = [col for col in columns if col not in conflict_targets]
            if update_cols:
                set_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_cols])
                conflict_clause = f"ON CONFLICT ({conflict_target_str}) DO UPDATE SET {set_clause}"
            else:
                conflict_clause = f"ON CONFLICT ({conflict_target_str}) DO NOTHING"
        else:
            conflict_clause = f"ON CONFLICT ({conflict_target_str}) DO NOTHING"
        
        query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders}) {conflict_clause}"
        
        for row in data:
            values = [row.get(col) for col in columns]
            cursor.execute(query, values)
        # values = [[row.get(col) for col in columns] for row in data]
        
        # extras.execute_values(cursor, query, values)
        print(f"  [+] Berhasil memuat {len(data)} baris ke tabel {table_name}.")

    def run(self):
        print("⚙️ Memulai proses Data Loading ke PostgreSQL...")
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()
                        
            print("\n-> Memproses Data Dimensi (DO NOTHING jika nama sudah ada)...")
            self._bulk_insert(cur, "Categories", ["category_id", "category_name"], self._load_json("categories.json"), ["category_name"], do_update=False)
            self._bulk_insert(cur, "Skin_Concerns", ["concern_id", "concern_name"], self._load_json("skin_concerns.json"), ["concern_name"], do_update=False)
            self._bulk_insert(cur, "Skin_Types", ["type_id", "type_name"], self._load_json("skin_types.json"), ["type_name"], do_update=False)
            
            print("\n-> Memproses Data Produk (DO UPDATE jika product_id sama)...")
            prod_cols = ["product_id", "clean_name", "brand", "why_we_love_it", "featured_ingredients_desc", "how_to_use", "batch_timestamp"]
            
            products_data = self._load_json("products.json")
            for row in products_data:
                if not row.get("batch_timestamp"):
                    row["batch_timestamp"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self._bulk_insert(cur, "Products", prod_cols, products_data, ["product_id"], do_update=True)
            
            print("\n-> Memproses Data SKUs & Ingredients...")
            sku_cols = ["sku_id", "product_id", "original_sku_name", "original_price", "sale_price"]
            self._bulk_insert(cur, "SKUs", sku_cols, self._load_json("skus.json"), ["sku_id"], do_update=True)
            
            ing_cols = ["ingredient_id", "sku_id", "liquid_variant", "ingredient_name"]
            self._bulk_insert(cur, "Ingredients", ing_cols, self._load_json("ingredients.json"), ["ingredient_id"], do_update=False)
            
            print("\n-> Memproses Relasi (DO NOTHING jika relasi sudah terbentuk)...")
            self._bulk_insert(cur, "Product_Category", ["product_id", "category_id"], self._load_json("product_category.json"), ["product_id", "category_id"], do_update=False)
            self._bulk_insert(cur, "Product_Concern", ["product_id", "concern_id"], self._load_json("product_concern.json"), ["product_id", "concern_id"], do_update=False)
            self._bulk_insert(cur, "Product_Type", ["product_id", "type_id"], self._load_json("product_type.json"), ["product_id", "type_id"], do_update=False)
            
            conn.commit()
            print("\n✓ DONE: Seluruh data berhasil dimuat ke dalam database secara permanen.")
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"\n✕ ERROR: Transaksi dibatalkan. {e}")
            sys.exit(1)
        finally:
            if conn:
                cur.close()
                conn.close()
                print("-> Koneksi database telah ditutup.")

if __name__ == "__main__":
    loader = OliveYoungDBDataLoader()
    loader.run()