import numpy as np, pandas as pd, sys

out = sys.argv[1]
rng = np.random.default_rng(42)

# product, category, base price, unit cost, true elasticity, base weekly units
products = [
    ("Espresso Beans 1kg",   "Beverages", 18.0,  9.0, -2.4, 520),
    ("Green Tea Box",        "Beverages",  7.5,  3.2, -1.9, 640),
    ("Cold Brew 6-pack",     "Beverages", 12.0,  6.0, -2.9, 410),
    ("Protein Bar 12ct",     "Snacks",    22.0, 12.5, -1.4, 380),
    ("Trail Mix 500g",       "Snacks",     9.0,  4.8, -1.7, 450),
    ("Dark Chocolate Pack",  "Snacks",     6.5,  2.9, -2.2, 700),
    ("Olive Oil 1L",         "Pantry",    15.0,  9.5, -0.8, 300),
    ("Basmati Rice 5kg",     "Pantry",    14.0,  9.0, -0.6, 350),
]

weeks = pd.date_range("2024-11-18", periods=104, freq="W-MON")
rows = []
for name, cat, p0, cost, e, q0 in products:
    # list price steps up/down a few times over two years
    n_changes = 4
    change_weeks = np.sort(rng.choice(np.arange(8, 100), n_changes, replace=False))
    list_mult = np.ones(len(weeks))
    cur = 1.0
    for cw in change_weeks:
        cur *= rng.choice([0.92, 0.95, 1.05, 1.08, 1.10])
        list_mult[cw:] = cur
    for i, w in enumerate(weeks):
        promo = rng.random() < 0.18
        disc = rng.choice([0.10, 0.15, 0.20, 0.25]) if promo else 0.0
        list_price = p0 * list_mult[i]
        price = round(list_price * (1 - disc), 2)
        comp_price = round(p0 * rng.normal(1.0, 0.05), 2)
        woy = w.isocalendar().week
        season = 0.12 * np.sin(2 * np.pi * (woy - 10) / 52) + (0.18 if woy >= 47 else 0.0)
        promo_lift = 0.15 if promo else 0.0       # display/feature lift beyond price
        comp_effect = 0.5 * np.log(comp_price / p0)  # cross-price effect
        logq = (np.log(q0) + e * np.log(price / p0) + promo_lift + season
                + comp_effect + rng.normal(0, 0.09))
        units = int(max(1, round(np.exp(logq))))
        rows.append(dict(week=w.date(), product=name, category=cat, price=price,
                         list_price=round(list_price, 2), promo=int(promo),
                         competitor_price=comp_price, unit_cost=cost,
                         units=units, revenue=round(units * price, 2),
                         true_elasticity=e))

df = pd.DataFrame(rows)
df.to_csv(out, index=False)
print(df.shape)
print(df.groupby("product")[["price", "units"]].agg(["mean", "std"]).round(2))
print(df.isna().sum().sum(), "missing")
