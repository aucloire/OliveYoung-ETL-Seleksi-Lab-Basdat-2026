'''
    Olive Young Global Web Scraper - Skincare Section (ETL)
    Script scraper.py ini melakukan ekstraksi, transformasi, dan loading data 
    dari e-commerce Olive Young Global (global.oliveyoung.com) menggunakan Selenium.
'''

import re
import os
import json
import time
import subprocess
import uuid
import uuid6
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class OliveYoungSkincareScraper:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.base_data_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(self.base_data_path, exist_ok=True)
        
        self._kill_chrome_processes()
        self.driver = self._init_driver()

        self.products_data = []
        self.skus_data = []
        self.ingredients_data = []
        self.dim_categories = {}
        self.dim_skin_concerns = {}
        self.dim_skin_types = {}
        self.rel_product_category = []
        self.rel_product_concern = []
        self.rel_product_type = []
        self.unique_product_urls = set()

    # FUNGSI & METODE UTILITAS
    def _kill_chrome_processes(self):
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/f', '/im', 'chromedriver.exe'], capture_output=True, check=False)
                print("Proses Chrome Windows dihentikan.")
            else:
                subprocess.run(['pkill', '-f', 'chromedriver'], capture_output=True, check=False)
                print("Proses Chrome Unix dihentikan.")
            time.sleep(2)
        except Exception as e:
            print(f"Gagal mematikan proses Chrome: {e}")

    def _init_driver(self) -> webdriver.Chrome:
        options = Options()
        options.page_load_strategy = 'eager'
        # options.add_argument('--headless=new') # hanya diaktifkan apabila tidak ingin menampilkan window chromedriver
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--incognito')
        options.add_argument('--disable-extensions')

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(10)
            print("WebDriver berhasil diinisialisasi.")
            return driver
        except Exception as e:
            print(f"Gagal membuat WebDriver: {e}")
            raise e
    
    def _delay(self):
        print("Menunggu 5 detik...")
        time.sleep(5)
    
    def _close_ad_popup(self):
        try:
            time.sleep(2) 
            close_btn = self.driver.find_element(By.XPATH, "/html/body/div[23]/div[2]/button")
            self.driver.execute_script("arguments[0].click();", close_btn)
            print("Iklan berhasil ditutup.")
            time.sleep(1)
        except Exception:
            pass
    
    def _get_text(self, xpath: str, default: str = "") -> str:
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            text_content = element.get_attribute("textContent")
            return re.sub(r'\s+', ' ', text_content).strip() if text_content else default
        except Exception:
            return default
    
    def _fix_sentence_spacing(self, text: str) -> str:
        if not text:
            return text
        return re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
    
    # FUNGSI & METODE PARSING & CLEANING
    def _clean_product_name(self, raw_name: str) -> str:
        clean_name = re.sub(r'\[.*?\]|\(.*?\)', '', raw_name)
        clean_name = re.sub(r'\d+\+\d+', '', clean_name)
        clean_name = re.sub(r'\b\d+(\.\d+)?\s*(ml|g|oz)\b', '', clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'\*?\s*\d+\s*ea\b', '', clean_name, flags=re.IGNORECASE)
        marketing_words = ['Double Set', 'Double Pack', 'Special Set', 'Refill Set', 'Set', 'Limited Edition', 'Exclusive', r'\*2ea']
        pattern = re.compile(r'\b(?:' + '|'.join(marketing_words) + r')\b', flags=re.IGNORECASE)
        clean_name = pattern.sub('', clean_name)
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        return re.sub(r'[-/&,]+$', '', clean_name).strip()
    
    def _parse_ingredients_structure(self, raw_ingredients: str, sku_id: str):
        clean_raw = "\n".join([line.strip() for line in raw_ingredients.split('\n') if line.strip()])

        if '[' in clean_raw and ']' in clean_raw:
            flat_raw = clean_raw.replace('\n', ' ')
            parts = re.split(r'\[(.*?)\]', flat_raw)

            if parts[0].strip():
                for ing in self._split_ingredients(parts[0]):
                    if ing.strip():
                        self.ingredients_data.append({
                            'ingredient_id': str(uuid6.uuid7()), 'sku_id': sku_id,
                            'liquid_variant': 'Main Formula', 'ingredient_name': ing.strip()
                        })

            for i in range(1, len(parts), 2):
                liquid_variant = parts[i].strip()
                if i + 1 < len(parts):
                    for ing in self._split_ingredients(parts[i+1]):
                        if ing.strip():
                            self.ingredients_data.append({
                                'ingredient_id': str(uuid6.uuid7()), 'sku_id': sku_id,
                                'liquid_variant': liquid_variant, 'ingredient_name': ing.strip()
                            })

        elif re.search(r'(?m)^\d+[\.\)]', clean_raw):
            lines = clean_raw.split('\n')
            liquid_variant = "Unknown Variant"
            
            for line in lines:
                match = re.match(r'^\d+[\.\)]\s*(.*)', line)
                
                if match:
                    liquid_variant = match.group(1).strip()
                else:
                    for ing in self._split_ingredients(line):
                        if ing.strip():
                            self.ingredients_data.append({
                                'ingredient_id': str(uuid6.uuid7()), 
                                'sku_id': sku_id,
                                'liquid_variant': liquid_variant, 
                                'ingredient_name': ing.strip()
                            })
        
        else:
            for ing in self._split_ingredients(clean_raw):
                if ing.strip():
                    self.ingredients_data.append({
                        'ingredient_id': str(uuid6.uuid7()), 'sku_id': sku_id,
                        'liquid_variant': 'Single Product', 'ingredient_name': ing.strip()
                    })
    
    def _split_ingredients(self, text: str) -> list:
        text = re.sub(r'(\d),(\d)', r'\1<NUM>\2', text)
        
        result = []
        current = []
        paren_depth = 0
        
        for char in text:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                if paren_depth > 0: paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                result.append("".join(current))
                current = []
            else:
                current.append(char)
        if current:
            result.append("".join(current))
            
        final_list = []
        for item in result:
            clean_item = item.replace('<NUM>', ',').strip()
            if clean_item:
                final_list.append(clean_item)
                
        return final_list
    
    # FUNGSI & METODE EKSTRAKSI
    def _extract_basic_metadata(self, url: str) -> tuple:
        brand = self._get_text("//a[@data-testid='product-brand-name']", "Unknown")
        raw_name = self._get_text("//dt[@data-testid='product-name']", "Unknown")
        clean_name = self._clean_product_name(raw_name)
        
        why_we_love_it = self._fix_sentence_spacing(self._get_text("//*[@data-testid='product-whyweloveit-content']"))
        featured_ingredients = self._fix_sentence_spacing(self._get_text("//*[@data-testid='product-featuredingredients-content']"))
        how_to_use = self._fix_sentence_spacing(self._get_text("//*[@data-testid='product-howtouse-content']"))
        
        match_id = re.search(r'prdtNo=([A-Za-z0-9]+)', url)
        product_id = match_id.group(1) if match_id else str(uuid6.uuid7())
        current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not any(p['product_id'] == product_id for p in self.products_data):
            self.products_data.append({
                'product_id': product_id, 'clean_name': clean_name, 'brand': brand,
                'why_we_love_it': why_we_love_it, 'featured_ingredients_desc': featured_ingredients,
                'how_to_use': how_to_use,
                'batch_timestamp': current_timestamp
            })
        return product_id, raw_name

    def _extract_pricing_metadata(self, product_id: str, raw_name: str) -> str:
        sale_price_str = self._get_text("//dd[@data-testid='product-price']//span[@class='notranslate']")
        try:
            sale_price_val = float(re.sub(r'[^\d.]', '', sale_price_str))
        except ValueError:
            sale_price_val = 0.0

        orig_price_str = self._get_text("//dt[@class='price']//div//span[@class='notranslate']")
        try:
            original_price_val = float(re.sub(r'[^\d.]', '', orig_price_str))
        except ValueError:
            original_price_val = sale_price_val

        sku_id = str(uuid6.uuid7())
        self.skus_data.append({
            'sku_id': sku_id, 'product_id': product_id,
            'original_sku_name': raw_name, 'original_price': original_price_val,
            'sale_price': sale_price_val
        })
        return sku_id
    
    def _extract_popup_ingredients(self, sku_id: str):
        try:
            info_btn = self.driver.find_element(By.XPATH, "//a[@data-attr='PD_specificItemPopup_click']")
            self.driver.execute_script("arguments[0].click();", info_btn)
            time.sleep(3) 
            ingredients_td = self.driver.find_element(By.XPATH, "//div[@id='modalSpecItemInformation']//table/tbody/tr[7]/td")
            ingredients_block = ingredients_td.get_attribute("textContent").strip()
            self._parse_ingredients_structure(ingredients_block, sku_id)      
        except Exception:
            pass
    
    # FUNGSI & METODE ETL PIPELINE UTAMA
    def harvest_filter_urls(self, filter_name: str, filter_xpath: str, accordion_xpath: str, rel_list: list, dim_dict: dict, dim_type: str, parent_xpath: str = None):
        print(f"\n--- MEMETAKAN FILTER: {filter_name} ---")
        
        print("-> Reset halaman...")
        self.driver.get(self.target_url)
        self._close_ad_popup()
        
        try:
            if accordion_xpath:
                try:
                    print("[+] Membuka dropdown...")
                    accordion_btn = self.driver.find_element(By.XPATH, accordion_xpath)
                    self.driver.execute_script("arguments[0].click();", accordion_btn)
                    time.sleep(2) 
                except Exception:
                    print("[-] Dropdown tidak ditemukan atau sudah terbuka.")

            if parent_xpath:
                try:
                    print("[v] Mengakses kategori utama...")
                    parent_li = self.driver.find_element(By.XPATH, parent_xpath)
                    clickable_parent = parent_li.find_element(By.XPATH, ".//label")
                    self.driver.execute_script("arguments[0].click();", clickable_parent)
                    
                    child_ul_xpath = f"{parent_xpath}/ul"
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, child_ul_xpath))
                    )
                    time.sleep(1)
                except Exception as e:
                    print(f" ! WARNING: Peringatan navigasi parent kategori: {e}")
            
            try:
                print(f"[v] Memilih filter '{filter_name}'...")
                filter_li = self.driver.find_element(By.XPATH, filter_xpath)
                clickable_filter = filter_li.find_element(By.XPATH, ".//label") 
                self.driver.execute_script("arguments[0].click();", clickable_filter)
                self._delay() 
            except Exception as e:
                print(f" ! WARNING: Peringatan klik filter: {e}")
            
            clicks = 0
            while clicks < 3: 
                print(f"-> Scan {(clicks + 1) * 24} katalog...")
                products_li = self.driver.find_elements(By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[6]/ul/li")
                
                new_urls_count = 0
                for li in products_li:
                    try:
                        href = li.find_element(By.XPATH, ".//a").get_attribute('href')
                        if href:
                            full_url = href if href.startswith('http') else f"https://global.oliveyoung.com{href}"
                            
                            if full_url not in self.unique_product_urls:
                                new_urls_count += 1

                            self.unique_product_urls.add(full_url)
                            
                            match_id = re.search(r'prdtNo=([A-Za-z0-9]+)', full_url)
                            product_id = match_id.group(1) if match_id else str(uuid6.uuid7())
                            
                            rel_record = {'product_id': product_id, f'{dim_type}_id': dim_dict[filter_name][f'{dim_type}_id']}
                            if rel_record not in rel_list:
                                rel_list.append(rel_record)
                    except Exception:
                        continue

                print(f"✓ DONE: Berhasil mengekstrak {len(products_li)} produk ({new_urls_count} URL baru).")
                if clicks < 2:
                    try:
                        more_btn = self.driver.find_element(By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[7]/p/button")
                        self.driver.execute_script("arguments[0].click();", more_btn)
                        self._delay()
                        clicks += 1
                    except Exception:
                        print(" ! WARNING: Tombol 'More' tidak ditemukan (asumsi: katalog habis).")
                        break
                else:
                    break
            print(f"✓ DONE: Selesai memetakan '{filter_name}'. Total antrean scraping: {len(self.unique_product_urls)} URL unik.")
        except Exception as e:
            print(f"✕ ERROR: Error memproses filter {filter_name}: {e}")

    def execute_mapping_pipeline(self):
        print("\n⚙️ Memulai Pemetaan Kategori & Filter")
        
        categories_map = {
            "Toner": {
                "parent": "/html/body/div[6]/div/div/div[1]/div[2]/div[3]/div[2]/ul/li[1]", # Moisturizers
                "xpath": "/html/body/div[6]/div/div/div[1]/div[2]/div[3]/div[2]/ul/li[1]/ul/li[1]"
            },
            "Essence & Serum": {
                "parent": "/html/body/div[6]/div/div/div[1]/div[2]/div[3]/div[2]/ul/li[1]", # Moisturizers
                "xpath": "/html/body/div[6]/div/div/div[1]/div[2]/div[3]/div[2]/ul/li[1]/ul/li[3]"
            },
            "Cream": {
                "parent": "/html/body/div[6]/div/div/div[1]/div[2]/div[3]/div[2]/ul/li[1]", # Moisturizers
                "xpath": "/html/body/div[6]/div/div/div[1]/div[2]/div[3]/div[2]/ul/li[1]/ul/li[4]"
            },
            "Cleansing Foams": {
                "parent": "/html/body/div[6]/div/div/div[1]/div[2]/div[3]/div[2]/ul/li[2]", # Cleansers
                "xpath": "/html/body/div[6]/div/div/div[1]/div[2]/div[3]/div[2]/ul/li[2]/ul/li[1]"
            }
        }
        categories_accordion = None

        concerns_map = {
            "Acne": "/html/body/div[6]/div/div/div[1]/div[2]/div[4]/div[2]/ul/li[1]",
            "Blackheads": "/html/body/div[6]/div/div/div[1]/div[2]/div[4]/div[2]/ul/li[3]",
            "Brightening": "/html/body/div[6]/div/div/div[1]/div[2]/div[4]/div[2]/ul/li[4]",
            "Moisturising": "/html/body/div[6]/div/div/div[1]/div[2]/div[4]/div[2]/ul/li[9]",
            "Soothing": "/html/body/div[6]/div/div/div[1]/div[2]/div[4]/div[2]/ul/li[13]",
            "Visible Pores": "/html/body/div[6]/div/div/div[1]/div[2]/div[4]/div[2]/ul/li[17]",
            "Well-aging": "/html/body/div[6]/div/div/div[1]/div[2]/div[4]/div[2]/ul/li[18]"
        }
        concerns_accordion = None
        
        types_map = {
            "Combination&Normal": "/html/body/div[6]/div/div/div[1]/div[2]/div[5]/div[2]/ul/li[1]",
            "Dry": "/html/body/div[6]/div/div/div[1]/div[2]/div[5]/div[2]/ul/li[2]",
            "Oily": "/html/body/div[6]/div/div/div[1]/div[2]/div[5]/div[2]/ul/li[3]",
            "Sensitive": "/html/body/div[6]/div/div/div[1]/div[2]/div[5]/div[2]/ul/li[4]"
        }
        types_accordion = "/html/body/div[6]/div/div/div[1]/div[2]/div[5]/div[1]/button"

        for name in categories_map.keys():
            self.dim_categories[name] = {'category_id': str(uuid.uuid5(uuid.NAMESPACE_DNS, name)), 'category_name': name}
        for name in concerns_map.keys():
            self.dim_skin_concerns[name] = {'concern_id': str(uuid.uuid5(uuid.NAMESPACE_DNS, name)), 'concern_name': name}
        for name in types_map.keys():
            self.dim_skin_types[name] = {'type_id': str(uuid.uuid5(uuid.NAMESPACE_DNS, name)), 'type_name': name}

        for name, data in categories_map.items():
            self.harvest_filter_urls(name, data['xpath'], categories_accordion, self.rel_product_category, self.dim_categories, 'category', parent_xpath=data['parent'])
            
        for name, xpath in concerns_map.items():
            self.harvest_filter_urls(name, xpath, concerns_accordion, self.rel_product_concern, self.dim_skin_concerns, 'concern')
            
        for name, xpath in types_map.items():
            self.harvest_filter_urls(name, xpath, types_accordion, self.rel_product_type, self.dim_skin_types, 'type')
        
    def extract_product_metadata(self):
        total_products = len(self.unique_product_urls)
        print(f"\n⚙️ Memulai ekstraksi metadata: {total_products} PRODUK DITEMUKAN")
        
        for index, url in enumerate(self.unique_product_urls, start=1):
            if index > 3:
                print("⚠️ [TEST MODE] Membatasi ekstraksi hanya 3 produk untuk keperluan screenshot scheduling.")
                break
            
            print(f"[{index}/{total_products}] Memproses: {url}")
            self.driver.get(url)
            self._close_ad_popup()
            self._delay()

            try:
                print(f"-> Mengekstrak brand dan nama produk...")
                product_id, raw_name = self._extract_basic_metadata(url)
                print(f"-> Mengekstrak harga produk...")
                sku_id = self._extract_pricing_metadata(product_id, raw_name)
                print(f"-> Mengekstrak komposisi produk...")
                self._extract_popup_ingredients(sku_id)
            except Exception as e:
                print(f"✕ ERROR: Error pada URL {url}: {e}")

    def export_datasets(self):
        print("\n⚙️ Menyimpan hasil ke folder data...")
        
        scraped_product_ids = {p['product_id'] for p in self.products_data}
        filtered_rel_category = [rel for rel in self.rel_product_category if rel['product_id'] in scraped_product_ids]
        filtered_rel_concern = [rel for rel in self.rel_product_concern if rel['product_id'] in scraped_product_ids]
        filtered_rel_type = [rel for rel in self.rel_product_type if rel['product_id'] in scraped_product_ids]
        
        datasets = {
            'categories.json': self.dim_categories, 'skin_concerns.json': self.dim_skin_concerns,
            'skin_types.json': self.dim_skin_types, 'products.json': self.products_data,
            'skus.json': self.skus_data, 'ingredients.json': self.ingredients_data,
            'product_category.json': filtered_rel_category, 'product_concern.json': filtered_rel_concern,
            'product_type.json': filtered_rel_type
        }

        for filename, data in datasets.items():
            full_path = os.path.join(self.base_data_path, filename)
            try:
                if isinstance(data, dict):
                    data = list(data.values())
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"✓ DONE: Berhasil diekspor: {filename}")
            except Exception as e:
                print(f"✕ ERROR: Gagal menyimpan {filename}: {e}")

    def run(self):
        try:
            self.execute_mapping_pipeline()
            self.extract_product_metadata()
            self.export_datasets()
            print("\n✓ DONE: Proses ETL selesai dengan sempurna!")
        except Exception as e:
            print(f"✕ ERROR: Scraper terhenti secara kritis: {e}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    TARGET_URL = "https://global.oliveyoung.com/display/category?ctgrNo=1000000008" 
    scraper = OliveYoungSkincareScraper(target_url=TARGET_URL)
    scraper.run()