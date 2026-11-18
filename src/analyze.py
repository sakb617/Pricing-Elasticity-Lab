import json, sys
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

src, out = sys.argv[1], sys.argv[2]
df = pd.read_csv(src, parse_dates=["week"])
df["woy"] = df["week"].dt.isocalendar().week.astype(int)
df["holiday"] = (df["woy"] >= 47).astype(int)
df["s1"] = np.sin(2 * np.pi * df["woy"] / 52)
df["c1"] = np.cos(2 * np.pi * df["woy"] / 52)
df["lq"] = np.log(df["units"])
df["lp"] = np.log(df["price"])
df["lcp"] = np.log(df["competitor_price"])

res = []
for name, g in df.groupby("product"):
    naive = smf.ols("lq ~ lp", g).fit()
    full = smf.ols("lq ~ lp + promo + lcp + holiday + s1 + c1", g).fit()
    e = full.params["lp"]
    lo, hi = full.conf_int().loc["lp"]
    cost = g["unit_cost"].iloc[0]
    # constant-elasticity demand anchored to the product's recent average
    recent = g.sort_values("week").tail(26)
    p_ref = float(recent["price"].mean())
    q_ref = float(recent["units"].mean())
    res.append(dict(
        product=name, category=g["category"].iloc[0], cost=float(cost),
        elasticity=float(e), ci_low=float(lo), ci_high=float(hi),
        naive_elasticity=float(naive.params["lp"]), r2=float(full.rsquared),
        true_elasticity=float(g["true_elasticity"].iloc[0]),
        p_ref=p_ref, q_ref=q_ref,
        promo_lift=float(np.exp(full.params["promo"]) - 1),
        cross_price=float(full.params["lcp"]),
    ))
r = pd.DataFrame(res)
print(r[["product", "true_elasticity", "naive_elasticity", "elasticity",
         "ci_low", "ci_high", "r2"]].round(2).to_string(index=False))
print("mean abs err naive:", (r.naive_elasticity - r.true_elasticity).abs().mean().round(3))
print("mean abs err full :", (r.elasticity - r.true_elasticity).abs().mean().round(3))
print("true inside CI:", int(((r.true_elasticity >= r.ci_low) & (r.true_elasticity <= r.ci_high)).sum()), "/", len(r))

# Profit simulation on a price grid (constant-elasticity demand)
mults = np.round(np.arange(0.70, 1.301, 0.02), 2)
for rec in res:
    e, c, p0, q0 = rec["elasticity"], rec["cost"], rec["p_ref"], rec["q_ref"]
    curve = []
    for m in mults:
        p = p0 * m
        q = q0 * (p / p0) ** e
        curve.append(dict(m=float(m), price=float(p), units=float(q),
                          revenue=float(p * q), profit=float((p - c) * q)))
    best = max(curve, key=lambda x: x["profit"])
    rec["curve"] = curve
    rec["best_mult"] = best["m"]
    rec["profit_now"] = float((p0 - c) * q0)
    rec["profit_best"] = best["profit"]
    # unconstrained optimum for elastic goods: p* = c * e / (1 + e)
    rec["theory_opt_price"] = float(c * e / (1 + e)) if e < -1 else None

# monthly + weekly series for charts
df["month"] = df["week"].dt.to_period("M").astype(str)
monthly = (df.groupby(["month", "category"])
             .agg(revenue=("revenue", "sum"), units=("units", "sum")).reset_index())
weekly = df[["week", "product", "price", "units", "promo"]].copy()
weekly["week"] = weekly["week"].dt.strftime("%Y-%m-%d")

summary = dict(
    total_revenue=float(df["revenue"].sum()),
    total_units=int(df["units"].sum()),
    avg_margin=float(((df["price"] - df["unit_cost"]) * df["units"]).sum() / df["revenue"].sum()),
    weeks=int(df["week"].nunique()), products=int(df["product"].nunique()),
    promo_share=float(df["promo"].mean()),
)
json.dump(dict(summary=summary, products=res,
               monthly=monthly.to_dict("records"),
               weekly=weekly.to_dict("records")), open(out, "w"))
print("wrote", out)
