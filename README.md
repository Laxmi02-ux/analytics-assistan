# Financial & Sales Analytics Assistant

A conversational analytics dashboard: ask plain-English business questions,
get back KPI cards, charts, and a next-month revenue forecast — built with
Flask, SQLite, pandas, and scikit-learn on the backend, and vanilla JS +
Chart.js on the frontend.

## What it does

- **Executive KPI cards**: total revenue, total profit, gross profit margin,
  ROI, and customer retention rate, computed on load.
- **Conversational querying**: type things like "Show revenue", "What's our
  ROI?", "Top 5 customers", or "Retention rate" and get a chart back.
- **Forecasting**: "Forecast next month" runs a linear regression over the
  historical monthly revenue to project the following month.
- **Financial ratios**: Gross Profit Margin (`Profit / Revenue x 100`) and
  ROI (`Profit / Cost x 100`) calculated per month from the SQL data.

## Project structure
analytics_assistant/
├── app.py # Flask backend: routes, SQL, ML, ratio calcs
├── requirements.txt
├── templates/
│ └── index.html # Dashboard + chat UI
└── static/
├── style.css # Dark-mode styling
└── app.js # Chat logic, KPI loading, Chart.js rendering


## Running it locally

```bash
cd analytics_assistant
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **https://analytics-assistan.onrender.com/** in your browser.

A `business_data.db` SQLite file will be created automatically on first run,
seeded with 6 months of sample sales data and 7 sample customers. Delete
that file if you want to reset the seed data.

## Design notes / honest caveats

A few things worth knowing (and mentioning if asked in an interview):

- **The "NLP parser" is keyword matching**, not a trained language model —
  it checks for words like "revenue", "roi", "forecast" in the message.
  This is a legitimate and common lightweight approach for a scoped chatbot,
  but it's not what most people mean by "NLP" in a research sense. A natural
  next step would be swapping in a small intent-classification model or a
  library like spaCy.
- **The forecast is a simple linear trend line** over 6 data points — good
  for demonstrating the scikit-learn workflow (`fit` → `predict`), but not
  a statistically robust forecast. With more historical data you'd want to
  account for seasonality (e.g., a SARIMA model or Prophet).
- **`debug=True` is for local development only.** If you ever deploy this
  (Render, Railway, PythonAnywhere, etc.), turn debug mode off — it exposes
  an interactive Python console over the network, which is a real security
  risk.
- **Customer data is randomly generated** (with a fixed random seed for
  reproducibility) since no real dataset was provided — swap in real data
  by editing the `init_db()` function in `app.py`.




  background (the *what* — which metrics matter) with a full-stack technical
  implementation (the *how* — Flask, SQL, pandas, scikit-learn, JS).
