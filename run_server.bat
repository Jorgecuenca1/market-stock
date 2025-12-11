@echo off
echo ========================================
echo   MARKET STOCK DASHBOARD
echo ========================================
echo.

REM Activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt -q

REM Create database tables
echo Creating database...
python manage.py migrate

REM Initialize stocks
echo Initializing stocks...
python manage.py init_stocks

REM Initial data update
echo Fetching initial data (this may take a minute)...
python manage.py update_data --all

REM Run server
echo.
echo ========================================
echo   Server starting at http://127.0.0.1:8000
echo   Press Ctrl+C to stop
echo ========================================
echo.
python manage.py runserver
