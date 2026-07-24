# Stock Analyzer

Stock Analyzer is a Flask-based web application for reviewing fundamental stock data and saving research over time. It is intended as a portfolio project that combines backend development, external API usage, authentication, persistence, and deployment practices in one product.

**Live Site:** https://www.onceingolconda.com/

## What this project does

Users can search for a company by name or ticker symbol and view core financial metrics such as:

- Forward P/E
- Earnings growth
- Profit margin
- Market capitalization
- Book value
- Price-to-book ratio
- Quick ratio
- Current ratio
- Free cash flow

The app also provides plain-language context around each metric so the analysis is easier to interpret for non-technical users.

## Core features

- Company lookup by ticker or company name
- Retrieval of live financial data through Yahoo Finance
- Fundamental analysis views for valuation, profitability, liquidity, and cash flow metrics
- User accounts with registration, login, password reset, and logout
- Persistent search history for authenticated users
- Update and delete actions for saved research entries
- Sortable history data for comparing financial metrics over time
- Guest access for basic exploration without creating an account

## Why this is a strong engineering showcase

This project goes beyond a simple demo app. It brings together several common engineering concerns in one product:

- Backend development with Flask and Python
- External API integration and data handling
- Authentication, session management, and secure password hashing
- Database design and persistence with SQLite (default; file-based `fundamentals.db` created automatically)
- Input validation and protection against common web vulnerabilities
- Deployment configuration for a production-style hosting environment

## Technical stack

- Backend: Python, Flask
- Database: SQLite (default; file-based `fundamentals.db` created automatically). Optional: PostgreSQL if you configure `DATABASE_URL` and adapt the code.
- Frontend: HTML, CSS, JavaScript, Jinja2
- Data source: Yahoo Finance via yfinance
- Authentication: bcrypt
- Deployment: Render with Gunicorn


## Project structure

- app.py: Flask routes, session handling, authentication flow, and database operations
- helpers.py: Database setup, session-based helpers, password validation, and history retrieval
- stockdata.py: Stock data retrieval and financial metric transformation
- company_check.py: Company name-to-ticker resolution
- templates/: User-facing HTML templates
- static/: CSS and JavaScript assets

## Finance angle

The app is intentionally centered around fundamental analysis rather than speculative trading. It highlights concepts that matter in investment research:

- Valuation metrics such as P/E and price-to-book
- Profitability and growth indicators
- Liquidity and balance sheet health
- Cash flow as a measure of business quality

That makes the project useful both as a software portfolio item and as a demonstration of financial literacy.

## Setup

### Prerequisites

- Python 3.10+
- A `.env` file with `SECRET_KEY` (the app creates a local SQLite database by default).

Optional: set `DATABASE_URL` if you intend to use PostgreSQL or another external database (the repository currently uses SQLite; switching to PostgreSQL requires updating the database connection code).

### Local development

1. Clone the repository and enter the project folder:

```bash
git clone <repo-url>
cd Fuatilia
```

2. Create and activate a virtual environment:

```bash
python -m venv Fuatilia
# Windows PowerShell
.\Fuatilia\Scripts\Activate.ps1
# macOS/Linux
source Fuatilia/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with at minimum a `SECRET_KEY`.

Example `.env` file in the project root (SQLite default):

```env
SECRET_KEY=your-secret-key
# Optional: DATABASE_URL=postgresql://username:password@host:5432/dbname
```

The app will create its required tables automatically on startup via the database initialization logic in `helpers.py` (it creates a local `fundamentals.db` by default).

5. Run the app locally:

```bash
python app.py
```

Then open the local URL shown by Flask, typically `http://127.0.0.1:5000/`.

### Production / deployment notes

The repository includes a Render configuration in `render.yaml` that starts the app with Gunicorn:

```yaml
services:
  - type: web
    name: stock-analyzer
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

For deployment, set `SECRET_KEY` in the host platform. If you plan to use an external database in production, set `DATABASE_URL` and adapt the app's DB connection accordingly; by default the app uses the local `fundamentals.db` SQLite file.

If you run locally with Gunicorn, you can use the command used in this workspace:

```bash
gunicorn app:app --bind 0.0.0.0:8000
```

## Notes

This is a portfolio-scale web application rather than a full trading platform. The current scope focuses on stock lookup, fundamental data presentation, user accounts, saved research history, and basic history management features.