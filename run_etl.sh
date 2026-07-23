#!/bin/bash
echo "======================================="
echo "[START] Olive Young Global ETL Pipeline"
echo "Start Time: $(date)"
echo "======================================="

# 1. SET WORKING DIRECTORY
cd "$(dirname "$0")" || exit
echo "Working Directory: $(pwd)"

# 2. CLEANUP CHROME
echo "Cleaning up Chrome processes..."
pkill -f chrome > /dev/null 2>&1
pkill -f chromedriver > /dev/null 2>&1
sleep 2

# 3. SETUP LOGGING
mkdir -p logs
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/etl_pipeline_${TIMESTAMP}.log"

echo "OLIVE YOUNG ETL PIPELINE STARTED" > "$LOG_FILE"
echo "Start Time: $(date)" >> "$LOG_FILE"
echo "Working Directory: $(pwd)" >> "$LOG_FILE"
echo "=======================================" >> "$LOG_FILE"

# 4. EKSEKUSI SCRAPING
echo ""
echo "[1/3] MENJALANKAN SCRAPING DATA..."
cd "Data Scraping/src" || exit
if python scraper.py >> "../../$LOG_FILE" 2>&1; then
    echo "SUCCESS: SCRAPING SELESAI"
    echo "[$(date +%T)] SCRAPING: SUCCESS" >> "../../$LOG_FILE"
else
    echo "ERROR: SCRAPING GAGAL"
    echo "[$(date +%T)] SCRAPING: FAILED" >> "../../$LOG_FILE"
    cd "../../" || exit
    exit 1
fi
cd "../../" || exit

# 5. EKSEKUSI STORING (LOADING OLTP)
echo ""
echo "[2/3] MENJALANKAN LOADING DATA KE POSTGRESQL..."
cd "Data Storing/src" || exit
if python loader.py >> "../../$LOG_FILE" 2>&1; then
    echo "SUCCESS: LOADING SELESAI"
    echo "[$(date +%T)] LOADING: SUCCESS" >> "../../$LOG_FILE"
else
    echo "ERROR: LOADING GAGAL"
    echo "[$(date +%T)] LOADING: FAILED" >> "../../$LOG_FILE"
fi
cd "../../" || exit

# 6. EKSEKUSI DATA WAREHOUSE (LOADING OLAP)
echo ""
echo "[3/3] MENJALANKAN LOADING DATA KE DATA WAREHOUSE (OLAP)..."
cd "Data Warehouse/src" || exit
if python dwh_loader.py >> "../../$LOG_FILE" 2>&1; then
    echo "SUCCESS: LOADING DWH SELESAI"
    echo "[$(date +%T)] LOADING DWH: SUCCESS" >> "../../$LOG_FILE"
else
    echo "ERROR: LOADING DWH GAGAL"
    echo "[$(date +%T)] LOADING DWH: FAILED" >> "../../$LOG_FILE"
fi
cd "../../" || exit

# 7. FINAL CLEANUP
pkill -f chrome > /dev/null 2>&1
pkill -f chromedriver > /dev/null 2>&1

echo ""
echo "======================================="
echo "[END] Olive Young Global ETL Pipeline"
echo "Log tersimpan di: $LOG_FILE"
echo "End Time: $(date)" >> "$LOG_FILE"
echo "======================================="