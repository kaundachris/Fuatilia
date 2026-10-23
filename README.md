# Fuatilia

Fuatilia ("to track/follow" in Swahili) is a web app for looking up US-listed companies and reviewing their key financials: a price chart, six valuation ratios, and the income statement, balance sheet and cash flow statement across several fiscal years. Data is pulled from [Financial Modeling Prep](https://financialmodelingprep.com/) (FMP). Registered users can save companies to a personal portfolio and sort them by ratio.

It was built as a project to learn programming from the ground up, with a focus on connecting a finance background to real code.

**Live demo:** https://www.fuatilia.com/

> Fuatilia displays data from a third-party API for learning and research purposes. It is not financial advice.

---

## Features

- **Search** for any US-listed company by name or ticker (NASDAQ, NYSE, AMEX). No account is needed to search or view a company.
- **View** a company's profile, price chart, valuation snapshot (P/E, P/B, operating profit margin, dividend yield, current ratio, debt-to-equity) and its three financial statements, with a tab for each statement.
- **Register and log in** with an email address and a password of at least 6 characters containing a letter, a number and a special character.
- **Save a search before you sign up.** If you look at a company while logged out, it is added to your portfolio when you register or log in.
- **Portfolio.** Saved companies appear in a table of the six ratios. Click a column header to sort ascending, and click again for descending.
- **Update** a saved company from the portfolio page to refresh its ratios, or **delete** it.
- **Change your password** (requires your current password) and **log out**.
- **Failed-login lockout.** After two failed attempts, the form is disabled and asks the user to contact support.
- **Local cache** so repeat visits don't use up API calls (see [How it works](#how-it-works)).

---

## Screenshots

**Index**: the search page

![Index page](static/images/Index%20Page.jpeg)

**Company page**: profile, price chart, valuation snapshot and financial statements

![Company page](static/images/Company%20Page.jpeg)

**Portfolio**: saved companies with sortable ratios

![Portfolio page](static/images/Portfolio%20Page.jpeg)

---

## Tech stack

| Layer | Tool |
|---|---|
| Backend | Python, Flask, served with Gunicorn in production |
| Templates | Jinja2, plain HTML and CSS, a few lines of JavaScript |
| Database | SQLite (`sqlite3` from the standard library) |
| Data source | Financial Modeling Prep API, called with `requests` |
| Data handling | pandas |
| Charts | Plotly (loaded from a CDN, so charts need an internet connection) |
| Auth | bcrypt for password hashing, Flask signed-cookie sessions |
| Config | python-dotenv |
| Analytics | Google tag, included in `base.html` |

---

## How it works

### Request flow

1. The user searches by name. `StockData.search()` queries FMP and keeps only results on US exchanges, removing duplicate symbols.
2. The user picks a company. `StockData.package_data()` gathers the profile, price history, income statement, balance sheet, cash flow statement and ratios.
3. The data is stored in SQLite, and the page is rendered with the statements and a Plotly price chart.
4. If the user is logged in and clicks **Add to portfolio**, a row containing the six headline ratios is saved to their portfolio. If they are logged out, the symbol is remembered for the session and saved when they register or log in.

### Caching

Different data goes stale at different speeds, so it is refreshed on different schedules:

| Data | Refetched from the API when |
|---|---|
| Company profile and price history | It has not been fetched today |
| Income statement, balance sheet, cash flow, ratios | The stored statement date is more than a year old, or nothing is stored |

Within those windows, pages are served from the local database. If one statement call fails while the others succeed, only the missing statement is fetched on the next visit.

This matters because the API plan has a daily call limit (see [Known limitations](#known-limitations)). A company page that needs a full refresh uses up to six API calls: two for profile and price, and four for statements and ratios. Each group of calls runs concurrently with a thread pool.

### Portfolio ratios are a snapshot

The ratios in a user's portfolio are copied from the ratios table at the moment the company is saved, so they reflect the data as it was then, not live values. Saving the same company again replaces the old row with fresh values.

The **Update** button on the portfolio page does the same for a saved company without searching for it again. It runs the normal caching check (so it only calls the API if the stored data is stale) and then copies the latest ratios into the portfolio row. Because statements and ratios are only refetched once the stored data is over a year old, Update will not change the ratios until a refetch is due.

### Database

SQLite with these tables:

- `users`: usernames (email addresses) and password hashes
- `companies`: profile and price data as JSON, plus the dates used for refresh checks
- `portfolios`: one row per user and company, holding the six saved ratios
- `income_statements`, `balance_sheets`, `cashflows` and `ratios`: one table each, with the data stored as JSON keyed by company

The schema is created automatically on first run.

---

## Design decisions

- **Passwords are hashed with bcrypt** using a per-password salt, and plaintext passwords are never stored. Login errors say "Invalid username or password" whether the username or the password was wrong, so they don't reveal which usernames exist.
- **All queries use parameters**, never string-built SQL for user values.
- **The sort column and order are whitelisted.** `ORDER BY` can't take a bound parameter, so the column and direction are checked against fixed lists before being placed in the query. Anything else falls back to the default.
- **Duplicates are prevented at the database level.** `UNIQUE(user_id, company_id)` on the portfolio table guarantees a user can't hold the same company twice, whatever the application code does.
- **Session cookies** are signed, set to `SameSite=Lax`, and marked `Secure` unless the app runs in debug mode.
- **Secrets come from the environment**, not from the code. `SECRET_KEY` and `API_KEY` live in `.env`, which is not committed.
- **Dates are validated and normalised** to ISO format before being stored, so every row is in the same format and date comparisons work on the text column.
- **API failures degrade gracefully.** If an endpoint returns nothing, the app stores what it has and shows an on-page message instead of crashing.

---

## Project structure

```
fuatilia/
├── app.py               # Flask routes: register, login, change, logout, search, company, portfolio, delete, update, sort
├── stock_data.py        # StockData class: calls the FMP API, builds the price chart, handles caching
├── helpers.py           # Database connection, schema setup, password check, portfolio storage, refresh checks
├── requirements.txt     # Pinned dependencies
├── .env.example         # Template for the environment variables
├── templates/
│   ├── base.html        # Shared page shell (header block, main block, footer)
│   ├── index.html       # Search landing page
│   ├── search.html      # Search results
│   ├── company.html     # Company profile and financial statements
│   ├── login.html / register.html / change.html
│   └── portfolio.html   # Saved companies, sortable
└── static/
    ├── index.css        # Single stylesheet for the whole app
    ├── index.js         # Fills in the footer's copyright year
    └── images/          # Screenshots used in this README, and the site icon
```

`fuatilia.db` is created on first run and is not committed.

---

## Getting started

### Prerequisites

- Python 3.14 (developed and tested on 3.14.7).
- A free API key from [Financial Modeling Prep](https://financialmodelingprep.com/).

### Install

1. Clone the repo and enter the folder.
2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   source .venv/bin/activate       # macOS / Linux
   ```
3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill it in (see below).
5. Run the app:
   ```
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser. The database is created automatically on first run.

### Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `API_KEY` | Yes | Your Financial Modeling Prep API key |
| `SECRET_KEY` | Yes | Secret used to sign session cookies. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_DEBUG` | Local only | Set to `1` when running locally. The app only marks its session cookie `Secure` when this is not `1`, and some browsers reject Secure cookies over plain `http://`, which would stop you staying logged in. **Never set this in production.** |
| `DB_PATH` | No | Path to the SQLite file. Defaults to `fuatilia.db` next to the code |

Example `.env` for local development:

```
API_KEY=your_fmp_api_key
SECRET_KEY=your_generated_secret_key
FLASK_DEBUG=1
```

---

## Deployment

The app is hosted on [Render](https://render.com/) and served with Gunicorn (for example, start command `gunicorn app:app`).

- **Persistent storage.** SQLite is a file, and Render's default filesystem is wiped on each deploy. Attach a persistent disk and point `DB_PATH` at a location on it, otherwise users and portfolios are lost on redeploy.
- **Set the environment variables** `API_KEY` and `SECRET_KEY` in the Render dashboard. Leave `FLASK_DEBUG` unset.
- **Pin the Python version.** Render picks its own Python unless told otherwise. Set the `PYTHON_VERSION` environment variable (or use a `.python-version` file) to match the version you develop on.
- Dependencies are installed from `requirements.txt`, so test upgrades locally before pushing.

---

## Known limitations

- **API call limit.** The FMP plan in use allows 250 calls a day, and a fully fresh company page can use up to six. Caching reduces this, but many new companies in one day could exhaust it.
- **Missing data looks the same whatever the cause.** Some symbols aren't available on the current API plan. A plan restriction, a failed call and a company with no data all show the same on-page message, and none of them is retried or rate-limited yet.
- **US exchanges only** (NASDAQ, NYSE, AMEX).
- **Login lockout is stored in the session cookie.** It slows down casual guessing, but it is not real brute-force protection, because clearing cookies resets it. Rate limiting by IP or account would be the proper fix.
- **No CSRF tokens on forms.** `SameSite=Lax` on the session cookie gives partial protection, but token-based protection (for example, Flask-WTF) is not implemented.
- **Actions re-render the page directly.** Opening a company, sorting, updating and deleting all respond to a POST, so refreshing the browser offers to resubmit, and a company page can't be bookmarked. Sort direction is a single flag per session rather than per column.
- **No automated tests.** The site is checked by hand.
- **SQLite** suits a small app with few concurrent users. A larger user base would call for a server database such as PostgreSQL.

---

## Acknowledgements

Financial data provided by [Financial Modeling Prep](https://financialmodelingprep.com/).
