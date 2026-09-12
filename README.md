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
