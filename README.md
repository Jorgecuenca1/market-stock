# Market Stock Dashboard

A comprehensive Django-based dashboard for real-time stock market analysis and news tracking.

## Features

- **Real-time Stock Data**: Track 8 key stocks (NVDA, AVGO, QCOM, LLY, GILD, CVX, GEV, ET)
- **Major Index Tracking**: S&P 500, NASDAQ 100, DOW JONES, Russell 2000, VIX
- **S&P 500 Analysis Report**: Detailed analysis with valuation metrics, balance sheet data, and ratings
- **News Aggregation**: Real-time news from multiple sources (Yahoo Finance, CNBC, MarketWatch, etc.)
- **Bilingual Support**: Switch between English and Spanish
- **Auto-refresh**: Data updates automatically every 5 minutes
- **Historical Data**: Stores and maintains historical price and news data

## Data Sources

- Yahoo Finance (primary - prices, fundamentals, news)
- GuruFocus (GF Score, Altman Z-Score)
- StockAnalysis.com (financial ratios)
- CNBC, MarketWatch, Benzinga (news)

## Quick Start

### Option 1: Use the batch file (Windows)
```batch
run_server.bat
```
This will install dependencies, set up the database, and start the server.

### Option 2: Manual setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up database**:
```bash
python manage.py migrate
```

3. **Initialize stocks**:
```bash
python manage.py init_stocks
```

4. **Fetch initial data**:
```bash
python manage.py update_data --all
```

5. **Start the server**:
```bash
python manage.py runserver
```

6. **Open browser**: http://127.0.0.1:8000

## Background Scheduler

For automatic updates, run the scheduler in a separate terminal:

```batch
run_scheduler.bat
```

Or manually:
```bash
python manage.py run_scheduler --price-interval 60 --news-interval 300 --analysis-interval 3600
```

## URLs

- `/` - Main Dashboard
- `/sp500-analysis/` - S&P 500 Analysis Report
- `/news-report/` - News Report
- `/stock/<SYMBOL>/` - Individual Stock Details
- `/set-language/en/` or `/set-language/es/` - Change language

## API Endpoints

- `GET /api/prices/` - Latest prices
- `GET /api/news/` - Latest news
- `GET /api/analysis/` - Latest analysis
- `POST /api/update/all/` - Trigger full update

## Management Commands

```bash
# Initialize stocks from settings
python manage.py init_stocks

# Update all data
python manage.py update_data --all

# Update specific data
python manage.py update_data --prices
python manage.py update_data --news
python manage.py update_data --analysis

# Run background scheduler
python manage.py run_scheduler
```

## Project Structure

```
market-stock/
├── market_stock/          # Django project settings
├── dashboard/             # Main dashboard app
│   ├── models.py          # Database models
│   ├── views.py           # Views
│   ├── urls.py            # URL routing
│   └── management/        # Custom commands
├── scraper/               # Data scraping app
│   ├── yahoo_finance.py   # Yahoo Finance scraper
│   ├── news_scraper.py    # News aggregator
│   ├── analysis_scraper.py # Analysis data scraper
│   └── services.py        # Scraping orchestration
├── templates/             # HTML templates
├── static/                # Static files
├── requirements.txt       # Python dependencies
└── manage.py
```

## Tracked Stocks

| Symbol | Name | Sector |
|--------|------|--------|
| NVDA | NVIDIA Corporation | Technology |
| AVGO | Broadcom Inc. | Technology |
| QCOM | Qualcomm Inc. | Technology |
| LLY | Eli Lilly & Co. | Healthcare |
| GILD | Gilead Sciences | Healthcare |
| CVX | Chevron Corporation | Energy |
| GEV | GE Vernova Inc. | Industrial |
| ET | Energy Transfer LP | Energy |

## Adding More Stocks

Edit `market_stock/settings.py`:

```python
TRACKED_STOCKS = [
    {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
    # Add more stocks here
]
```

Then run:
```bash
python manage.py init_stocks
python manage.py update_data --all
```

## License

For educational and personal use only. Not financial advice.
