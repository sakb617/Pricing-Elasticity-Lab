# Pricing Elasticity Lab

A pricing strategy analysis project: estimate how demand responds to price for eight products, then simulate revenue and profit under different price changes.

The data is **synthetic**. It is generated with known price elasticities, so every estimate can be checked against the truth.

## What it shows
- **Elasticity per product.** A price-only regression is biased by promotions. Adding controls (promo, competitor price, season) cuts the average error from about 0.43 to 0.08, and the true value falls inside the 95% interval for 7 of 8 products.
- **Price simulator.** Revenue and profit under any price change from -30% to +30%, using constant-elasticity demand around each product's 26-week average.
- **Recommendations.** The profit-maximizing move per product, within a cap you choose (about +6.4% gross profit at a 15% cap).

## Dashboards
- Web version: `dashboard/index.html` (open it in a browser, or enable GitHub Pages)
- Tableau Public: https://public.tableau.com/app/profile/sakshi.bhardwaj5595/viz/pricingelasticity_17950171420420/Dashboard1
- Screenshot: <img width="1440" height="900" alt="screenshot-dashboard" src="https://github.com/user-attachments/assets/b8bb39a7-24b9-439d-b9e8-a3c8cec0f992" />


## Run it yourself
```bash
pip install numpy pandas statsmodels
python src/generate_data.py data/sales_weekly.csv
python src/analyze.py data/sales_weekly.csv results.json
```

## Files
| File | What it is |
|---|---|
| `data/sales_weekly.csv` | 832 rows, one per product per week |
| `data/product_elasticity.csv` | Per-product estimates, intervals, cost, reference price |
| `data/price_grid.csv` | Each product at every price change from -30% to +30% |
| `src/generate_data.py` | Builds the synthetic dataset |
| `src/analyze.py` | Estimates elasticities and runs the profit simulation |

## Limits
Profit is gross profit (price minus unit cost, times units). Fixed costs, cannibalization between products and competitor reactions are not modeled. Prices outside the observed range are extrapolations.
