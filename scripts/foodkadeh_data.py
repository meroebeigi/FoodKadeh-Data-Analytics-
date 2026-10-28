"""Canonical synthetic dataset shared by the notebook and SQL exporter."""
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

def generate_data(seed=42):
    """Return the six-month demo tables without changing NumPy's global RNG."""
    rng = np.random.RandomState(seed)
    start_date = pd.Timestamp("2025-09-01")
    end_date   = pd.Timestamp("2026-02-28")
    dates      = pd.date_range(start_date, end_date, freq="D")

    n_users    = 2500
    n_products = 120

    cities               = ["Tehran", "Shiraz", "Isfahan", "Tabriz", "Mashhad"]
    acquisition_channels = ["Organic Search", "Instagram Ads", "Referral", "Google Ads", "Direct"]
    product_categories   = ["Restaurant Meal", "Grocery", "Bakery", "Beverage", "Snack", "Healthy Food"]
    age_groups           = ["18-24", "25-34", "35-44", "45-54", "55+"]

    # ── Users ──────────────────────────────────────────────────────────────────
    # Synthetic signup weights; no marketing-spend data is generated.
    signup_weights = np.concatenate([
        np.ones(30) * 1.0,  # Sep
        np.ones(31) * 1.2,  # Oct
        np.ones(30) * 1.5,  # Nov
        np.ones(31) * 2.0,  # Dec (peak)
        np.ones(31) * 1.8,  # Jan
        np.ones(28) * 1.6,  # Feb
    ])
    signup_weights = signup_weights / signup_weights.sum()

    users = pd.DataFrame({
        "user_id":  np.arange(1, n_users + 1),
        "signup_date": rng.choice(dates, size=n_users, replace=True, p=signup_weights),
        "city":          rng.choice(cities, size=n_users, p=[0.45, 0.15, 0.15, 0.10, 0.15]),
        "acquisition_channel": rng.choice(acquisition_channels, size=n_users,
                                                  p=[0.30, 0.25, 0.18, 0.17, 0.10]),
        "age_group": rng.choice(age_groups, size=n_users, p=[0.24, 0.38, 0.22, 0.11, 0.05]),
    })
    users["signup_month"] = users["signup_date"].dt.to_period("M").astype(str)

    # ── Products ──────────────────────────────────────────────────────────────
    category_prices = {
        "Restaurant Meal": (8, 35),
        "Grocery":         (5, 50),
        "Bakery":          (3, 15),
        "Beverage":        (2, 12),
        "Snack":           (2, 10),
        "Healthy Food":    (6, 28),
    }
    product_cats = rng.choice(product_categories, size=n_products,
                                    p=[0.42, 0.23, 0.12, 0.10, 0.08, 0.05])
    base_prices = np.array([
        round(rng.uniform(*category_prices[c]), 2) for c in product_cats
    ])
    products = pd.DataFrame({
        "product_id": np.arange(1, n_products + 1),
        "category":   product_cats,
        "base_price": base_prices,
    })

    # ── Sessions ──────────────────────────────────────────────────────────────
    n_sessions = 22000

    # Sample candidate session dates uniformly; remove pre-signup sessions below.
    session_dates = rng.choice(dates, size=n_sessions)

    sessions = pd.DataFrame({
        "session_id":     np.arange(1, n_sessions + 1),
        "user_id":        rng.choice(users["user_id"], size=n_sessions),
        "session_date":   session_dates,
        "device":         rng.choice(["Mobile", "Desktop", "Tablet"],
                                            size=n_sessions, p=[0.78, 0.18, 0.04]),
        "traffic_source": rng.choice(acquisition_channels, size=n_sessions,
                                            p=[0.32, 0.26, 0.14, 0.18, 0.10]),
    })

    sessions = sessions.merge(users[["user_id", "signup_date"]], on="user_id", how="left")
    sessions = sessions[sessions["session_date"] >= sessions["signup_date"]].copy().reset_index(drop=True)
    sessions["session_id"] = np.arange(1, len(sessions) + 1)

    channel_cvr = {"Organic Search": 0.16, "Instagram Ads": 0.13,
                   "Referral": 0.22, "Google Ads": 0.15, "Direct": 0.20}
    device_cvr  = {"Mobile": 0.02, "Desktop": 0.00, "Tablet": -0.02}

    base_prob   = sessions["traffic_source"].map(channel_cvr)
    device_adj  = sessions["device"].map(device_cvr)
    conv_prob   = np.clip(base_prob + device_adj, 0.04, 0.35)
    sessions["converted"] = rng.binomial(1, conv_prob)

    # ── Orders ────────────────────────────────────────────────────────────────
    converted = sessions[sessions["converted"] == 1].copy()
    orders = converted[["session_id", "user_id", "session_date"]].rename(
        columns={"session_date": "order_date"}).reset_index(drop=True)
    orders["order_id"] = np.arange(1, len(orders) + 1)

    # Delivery fee drops slightly as platform matures
    day_idx = (orders["order_date"] - start_date).dt.days
    orders["delivery_fee"] = np.round(
        rng.uniform(0.8, 3.5, size=len(orders)) - day_idx * 0.002, 2
    ).clip(0.5, 3.5)

    # Larger simulated discounts in Sep-Nov; this applies to all orders then.
    discount_rate = np.where(
        orders["order_date"] < pd.Timestamp("2025-12-01"),
        rng.uniform(0, 6, len(orders)),
        rng.uniform(0, 3, len(orders))
    )
    orders["discount"] = np.round(discount_rate, 2)
    orders["status"]   = rng.choice(
        ["Completed", "Cancelled", "Refunded"],
        size=len(orders), p=[0.88, 0.08, 0.04]
    )

    # Delivery time with a simulated random delay; no time-of-day field exists
    orders["delivery_time_min"] = np.clip(
        rng.normal(32, 8, len(orders)) +
        rng.choice([0, 15], size=len(orders), p=[0.7, 0.3]),  # rush hour
        15, 90
    ).round(1)

    # ── Order Items ───────────────────────────────────────────────────────────
    items_list = []
    for _, row in orders.iterrows():
        n_items = rng.choice([1, 2, 3, 4, 5], p=[0.42, 0.28, 0.18, 0.08, 0.04])
        sel     = rng.choice(products["product_id"], size=n_items, replace=False)
        for pid in sel:
            qty       = rng.choice([1, 2, 3], p=[0.78, 0.18, 0.04])
            bp        = products.loc[products["product_id"] == pid, "base_price"].values[0]
            # Slight weekend premium
            weekend   = row["order_date"].weekday() >= 5
            price     = round(bp * rng.uniform(0.95, 1.10) * (1.05 if weekend else 1.0), 2)
            items_list.append({
                "order_id":    row["order_id"],
                "product_id":  pid,
                "quantity":    qty,
                "unit_price":  price,
                "item_revenue": round(price * qty, 2),
            })

    order_items = pd.DataFrame(items_list)

    order_revenue = order_items.groupby("order_id", as_index=False)["item_revenue"].sum()
    orders = orders.merge(order_revenue, on="order_id", how="left")
    orders["gross_revenue"] = orders["item_revenue"] + orders["delivery_fee"]
    orders["net_revenue"]   = orders["gross_revenue"] - orders["discount"]
    orders.loc[orders["status"] != "Completed", ["gross_revenue", "net_revenue"]] = 0

    # Merge user info
    orders = orders.merge(users[["user_id", "city", "acquisition_channel",
                                   "age_group", "signup_date"]], on="user_id", how="left")

    completed = orders[orders["status"] == "Completed"].copy()

    return {name: value for name, value in locals().items()
            if name in ('users', 'products', 'sessions', 'orders', 'order_items',
                        'completed', 'start_date', 'end_date')}

def analytics_view(tables, view):
    """Evaluate the repository SQL against in-memory source tables."""
    allowed = {'customer_rfm', 'cohort_retention', 'channel_conversion',
               'category_sales', 'monthly_kpis'}
    if view not in allowed:
        raise ValueError(view)
    with sqlite3.connect(':memory:') as db:
        for name in ('users', 'products', 'sessions', 'orders', 'order_items'):
            frame = tables[name].copy()
            for col in frame:
                if col.endswith('_date'):
                    frame[col] = pd.to_datetime(frame[col]).dt.strftime('%Y-%m-%d')
            frame.to_sql(name, db, index=False)
        db.executescript((Path(__file__).resolve().parents[1] / 'sql/01_analytics.sql').read_text(encoding='utf-8'))
        return pd.read_sql_query(f'SELECT * FROM {view}', db)
