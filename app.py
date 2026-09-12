"""
AI-Powered Financial & Sales Analytics Assistant
--------------------------------------------------
A Flask backend that combines:
  1. A simple rule-based intent parser (keyword matching, described honestly
     as "intent detection" rather than true NLP)
  2. SQL queries against a local SQLite database of sales + customer data
  3. A scikit-learn Linear Regression model for next-month revenue forecasting
  4. Basic financial ratio calculations (Gross Profit Margin, ROI, Retention)

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template
import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
DB_PATH = "business_data.db"


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            month_id INTEGER,
            month TEXT,
            revenue REAL,
            cost REAL,
            profit REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER,
            name TEXT,
            month_id INTEGER,
            revenue REAL,
            retained INTEGER
        )
    """)

    # Seed sales data only if empty
    cur.execute("SELECT COUNT(*) FROM sales")
    if cur.fetchone()[0] == 0:
        sample_sales = [
            (1, "Jan", 45000, 31000, 14000),
            (2, "Feb", 52000, 35500, 16500),
            (3, "Mar", 61000, 40000, 21000),
            (4, "Apr", 58000, 39000, 19000),
            (5, "May", 72000, 47000, 25000),
            (6, "Jun", 85000, 53000, 32000),
        ]
        cur.executemany(
            "INSERT INTO sales VALUES (?,?,?,?,?)", sample_sales
        )

    # Seed customer data only if empty
    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] == 0:
        names = ["Acme Corp", "Bluepeak Ltd", "Coral Traders", "Delta Foods",
                  "Everest Textiles", "Falcon Retail", "Ganga Logistics"]
        rng = np.random.default_rng(42)
        rows = []
        cid = 1
        for name in names:
            for month_id in range(1, 7):
                revenue = round(float(rng.uniform(2000, 15000)), 2)
                retained = 1 if rng.random() > 0.15 else 0
                rows.append((cid, name, month_id, revenue, retained))
            cid += 1
        cur.executemany(
            "INSERT INTO customers VALUES (?,?,?,?,?)", rows
        )

    conn.commit()
    conn.close()


init_db()


# ---------------------------------------------------------------------------
# Helper: financial ratio calculations
# ---------------------------------------------------------------------------
def gross_profit_margin(revenue, profit):
    if revenue == 0:
        return 0.0
    return (profit / revenue) * 100


def roi(profit, cost):
    if cost == 0:
        return 0.0
    return (profit / cost) * 100


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/kpis", methods=["GET"])
def kpis():
    """Executive summary cards shown on dashboard load."""
    conn = get_conn()
    sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
    cust_df = pd.read_sql_query("SELECT * FROM customers", conn)
    conn.close()

    total_revenue = sales_df["revenue"].sum()
    total_profit = sales_df["profit"].sum()
    total_cost = sales_df["cost"].sum()
    avg_margin = gross_profit_margin(total_revenue, total_profit)
    avg_roi = roi(total_profit, total_cost)

    latest_month = cust_df["month_id"].max()
    latest = cust_df[cust_df["month_id"] == latest_month]
    retention_rate = (latest["retained"].sum() / len(latest)) * 100 if len(latest) else 0

    return jsonify({
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "gross_margin_pct": round(avg_margin, 2),
        "roi_pct": round(avg_roi, 2),
        "retention_pct": round(retention_rate, 2),
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    user_msg = (request.json or {}).get("message", "").lower()
    conn = get_conn()

    # --- Intent: revenue / sales trend ---
    if "revenue" in user_msg or ("sales" in user_msg and "forecast" not in user_msg):
        df = pd.read_sql_query("SELECT month, revenue FROM sales", conn)
        conn.close()
        return jsonify({
            "reply": "Here's the revenue trend over the past 6 months:",
            "type": "chart",
            "chart_type": "line",
            "labels": df["month"].tolist(),
            "data": df["revenue"].tolist(),
            "metric": "Revenue ($)",
        })

    # --- Intent: profit trend ---
    if "profit" in user_msg and "margin" not in user_msg:
        df = pd.read_sql_query("SELECT month, profit FROM sales", conn)
        conn.close()
        return jsonify({
            "reply": "Here's the profit trend over the past 6 months:",
            "type": "chart",
            "chart_type": "line",
            "labels": df["month"].tolist(),
            "data": df["profit"].tolist(),
            "metric": "Profit ($)",
        })

    # --- Intent: gross profit margin ---
    if "margin" in user_msg:
        df = pd.read_sql_query("SELECT month, revenue, profit FROM sales", conn)
        conn.close()
        df["margin"] = df.apply(
            lambda r: gross_profit_margin(r["revenue"], r["profit"]), axis=1
        )
        return jsonify({
            "reply": "Here's the Gross Profit Margin trend (Profit / Revenue x 100):",
            "type": "chart",
            "chart_type": "bar",
            "labels": df["month"].tolist(),
            "data": [round(v, 2) for v in df["margin"].tolist()],
            "metric": "Gross Profit Margin (%)",
        })

    # --- Intent: ROI ---
    if "roi" in user_msg or "return on investment" in user_msg:
        df = pd.read_sql_query("SELECT month, profit, cost FROM sales", conn)
        conn.close()
        df["roi"] = df.apply(lambda r: roi(r["profit"], r["cost"]), axis=1)
        avg_roi = df["roi"].mean()
        return jsonify({
            "reply": f"Average ROI over the period is **{avg_roi:.2f}%** "
                     f"(calculated as Profit / Cost x 100 per month).",
            "type": "chart",
            "chart_type": "bar",
            "labels": df["month"].tolist(),
            "data": [round(v, 2) for v in df["roi"].tolist()],
            "metric": "ROI (%)",
        })

    # --- Intent: forecast / predict ---
    if "predict" in user_msg or "forecast" in user_msg:
        df = pd.read_sql_query("SELECT month_id, revenue FROM sales", conn)
        conn.close()

        X = df[["month_id"]]
        y = df["revenue"]
        model = LinearRegression().fit(X, y)

        next_month_id = int(df["month_id"].max()) + 1
        prediction = model.predict(np.array([[next_month_id]]))[0]

        return jsonify({
            "reply": f"Based on a linear regression over the last "
                     f"{len(df)} months, projected revenue for the next "
                     f"month is **${prediction:,.2f}**. "
                     f"(Note: this is a simple trend line, not a "
                     f"seasonally-adjusted forecast.)",
            "type": "text",
        })

    # --- Intent: top customers ---
    if "top customer" in user_msg or "top 5" in user_msg or "best customer" in user_msg:
        df = pd.read_sql_query(
            "SELECT name, SUM(revenue) as total_revenue FROM customers "
            "GROUP BY name ORDER BY total_revenue DESC LIMIT 5",
            conn,
        )
        conn.close()
        lines = "\n".join(
            f"{i+1}. {row['name']} — ${row['total_revenue']:,.2f}"
            for i, row in df.iterrows()
        )
        return jsonify({
            "reply": f"Top 5 customers by total revenue:\n{lines}",
            "type": "chart",
            "chart_type": "bar",
            "labels": df["name"].tolist(),
            "data": [round(v, 2) for v in df["total_revenue"].tolist()],
            "metric": "Customer Revenue ($)",
        })

    # --- Intent: retention ---
    if "retention" in user_msg or "churn" in user_msg:
        df = pd.read_sql_query("SELECT month_id, retained FROM customers", conn)
        conn.close()
        monthly = df.groupby("month_id")["retained"].mean() * 100
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        return jsonify({
            "reply": "Here's the customer retention rate by month:",
            "type": "chart",
            "chart_type": "line",
            "labels": months[:len(monthly)],
            "data": [round(v, 2) for v in monthly.tolist()],
            "metric": "Retention Rate (%)",
        })

    # --- Fallback ---
    conn.close()
    return jsonify({
        "reply": (
            "I can help with: revenue trends, profit trends, gross profit "
            "margin, ROI, sales forecasts, top customers, or retention "
            "rate. Try asking something like 'What's our ROI?' or "
            "'Forecast next month's revenue'."
        ),
        "type": "text",
    })


if __name__ == "__main__":
    # debug=True is fine for local development only.
    # Never deploy with debug=True — it exposes an interactive
    # Python console over the network.
    app.run(debug=True)
