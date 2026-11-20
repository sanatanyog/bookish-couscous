# Reko Diq: illustrative economic-risk analysis

A reproducible 10,000-scenario Monte Carlo stress test of Reko Diq's net present value (NPV). The model explores sensitivity to copper prices, capital overruns, construction delays, operating shocks and discount rates.

**This is an illustrative surrogate, not Barrick's project cash-flow model or an investment forecast.** Its scenario distributions are analyst assumptions, not estimated probabilities from historical data. The share of negative-NPV draws must not be described as the objective probability that the mine will fail.

## Results

| Measure | Result |
|---|---:|
| Scenarios | 10,000 |
| Mean NPV | +$1.88 billion |
| Median NPV | +$1.81 billion |
| Negative-NPV scenarios | 40.2% |
| 5th-percentile NPV | −$10.04 billion |
| 95th-percentile NPV | +$13.88 billion |

The results are reproducible using seed `20261120`. They do not establish a frequentist p-value or test an empirical population of mining projects.

## Run

Python 3.10 or later:

```bash
python -m pip install -r requirements.txt
python -m src.reko_analysis
python -m unittest discover -s tests -v
```

The script writes `results/summary.csv`, `results/scenarios.csv`, `results/npv_distribution.png` and `results/sensitivity.png`. Use `--output path`, `--draws N` or `--seed N` to change defaults.

## Files

- [`src/reko_analysis.py`](src/reko_analysis.py): model and plots
- [`methodology/Reko_Diq_Monte_Carlo_Assessment.pdf`](methodology/Reko_Diq_Monte_Carlo_Assessment.pdf): assumptions, interpretation and limitations
- [`results/summary.csv`](results/summary.csv): reproducible summary statistics
- [`results/scenarios.csv`](results/scenarios.csv): scenario-level output
- [`tests/test_model.py`](tests/test_model.py): reproducibility checks

## Assumptions

| Input | Distribution or proxy |
|---|---|
| Copper price | Normal($3.85/lb, $0.70), clipped to $2–$6.50 |
| Capital overrun | Triangular(0%, 18%, 65%), applied to $8.83bn |
| Construction delay | 0–5 years with assumed discrete probabilities |
| Operating shock | Normal(0, $1.5bn) NPV equivalent |
| Discount rate | Normal(10%, 1.8 percentage points), clipped to 7–16% |
| Operating value proxy | $21.83bn; 11-year discount duration |
| Dependence | Independent inputs; material limitation |

The model uses two **rounded** published NPV anchors: approximately $13bn for the reference commodity-price case and approximately $4bn for a lower-price case. **The lower-price case also assumes a lower gold price**, but the surrogate varies only copper explicitly. The fitted copper slope therefore absorbs some gold-price differences. It must not be interpreted as Barrick's estimated copper-only sensitivity. Taxes, royalties, detailed annual cash flows and security impacts are not modeled separately.

## Primary sources

- [Barrick, Reko Diq Technical Report (2025)](https://s25.q4cdn.com/322814910/files/doc_downloads/reko_diq/Barrick_RekoDiq_TechnicalReport_20241231.pdf), Table 22-5
- [Barrick, Reko Diq project update (April 2026)](https://www.barrick.com/English/news/news-details/2026/barrick-provides-an-update-on-reko-diq/default.aspx)

The published technical report is an external source, not reproduced or redistributed here.
