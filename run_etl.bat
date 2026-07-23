@echo off
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo =======================================
echo [START] Olive Young Global ETL Pipeline 
echo Start Time: %date% %time%
echo =======================================

REM 1. SET WORKING DIRECTORY
cd /d "%~dp0"
echo Working Directory: %CD%

set PYTHON_EXE="C:\Users\USER\miniconda3\python.exe"

REM 2. KILL CHROME PROCESSES
echo Cleaning up Chrome processses...
taskkill /f /im chromedriver.exe >nul 2>&1
timeout /t 2 >nul

REM 3. SETUP LOGGING
if not exist "logs" mkdir "logs"
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=logs\etl_pipeline_%TIMESTAMP%.log

echo > "%LOG_FILE%"
echo OLIVE YOUNG ETL PIPELINE STARTED >> "%LOG_FILE%"
echo Start Time: %date% %time% >> "%LOG_FILE%"
echo Working Directory: %CD% >> "%LOG_FILE%"
echo ======================================= >> "%LOG_FILE%"

REM 4. EKSEKUSI SCRAPING
echo.
echo [1/3] MENJALANKAN SCRAPING DATA...
cd "Data Scraping\src"
%PYTHON_EXE% scraper.py >> "..\..\%LOG_FILE%" 2>&1
set SCRAPE_RESULT=%errorlevel%

if %SCRAPE_RESULT% equ 0 (
    echo SUCCESS: SCRAPING SELESAI
    echo [%time%] SCRAPING: SUCCESS >> "..\..\%LOG_FILE%"
) else (
    echo ERROR: SCRAPING GAGAL - Exit Code: %SCRAPE_RESULT%
    echo [%time%] SCRAPING: FAILED [Exit Code: %SCRAPE_RESULT%] >> "..\..\%LOG_FILE%"
    cd "..\..\"
    goto end
)
cd "..\..\"

REM 5. EKSEKUSI STORING (LOADING OLTP)
echo.
echo [2/3] MENJALANKAN LOADING DATA KE POSTGRESQ (OLTP)...
cd "Data Storing\src"
%PYTHON_EXE% loader.py >> "..\..\%LOG_FILE%" 2>&1
set LOAD_RESULT=%errorlevel%

if %LOAD_RESULT% equ 0 (
    echo SUCCESS: LOADING SELESAI
    echo [%time%] LOADING: SUCCESS >> "..\..\%LOG_FILE%"
) else (
    echo ERROR: LOADING GAGAL - Exit Code: %LOAD_RESULT%
    echo [%time%] LOADING: FAILED [Exit Code: %LOAD_RESULT%] >> "..\..\%LOG_FILE%"
)
cd "..\..\"

REM 6. EKSEKUSI DATA WAREHOUSE (LOADING OLAP)
echo.
echo [3/3] MENJALANKAN LOADING DATA KE DATA WAREHOUSE (OLAP)...
cd "Data Warehouse\src"
%PYTHON_EXE% dwh_loader.py >> "..\..\%LOG_FILE%" 2>&1
set DWH_RESULT=%errorlevel%

if %DWH_RESULT% equ 0 (
    echo SUCCESS: LOADING DWH SELESAI
    echo [%time%] LOADING DWH: SUCCESS >> "..\..\%LOG_FILE%"
) else (
    echo ERROR: LOADING DWH GAGAL - Exit Code: %DWH_RESULT%
    echo [%time%] LOADING DWH: FAILED [Exit Code: %DWH_RESULT%] >> "..\..\%LOG_FILE%"
)
cd "..\..\"

:end
REM 7. FINAL CLEANUP
echo.
echo Membersihkan sisa proses background...
taskkill /f /im chromedriver.exe >nul 2>&1

echo =======================================
echo [END] ETL Pipeline
echo Log tersimpan di: %LOG_FILE% 
echo End Time: %date% %time% >> "%LOG_FILE%"
echo =======================================