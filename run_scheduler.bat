@echo off
echo ========================================
echo   MARKET STOCK - BACKGROUND SCHEDULER
echo ========================================
echo.
echo This will run automatic updates:
echo   - Prices: every 1 minute
echo   - News: every 5 minutes
echo   - Analysis: every 1 hour
echo.
echo Press Ctrl+C to stop
echo.

REM Activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

python manage.py run_scheduler --price-interval 60 --news-interval 300 --analysis-interval 3600
