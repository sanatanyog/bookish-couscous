"""Illustrative Reko Diq NPV stress test. Not a project cash-flow forecast."""

from pathlib import Path
import argparse
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

SEED = 20261120
DRAWS = 10_000


def simulate(n=DRAWS, seed=SEED):
    rng = np.random.default_rng(seed)
    copper = np.clip(rng.normal(3.85, 0.70, n), 2.0, 6.5)
    overrun = np.clip(rng.triangular(0, 0.18, 0.65, n), 0, 0.85)
    delay = rng.choice([0, 1, 2, 3, 4, 5], n, p=[.10, .20, .27, .23, .14, .06])
    operating_shock = rng.normal(0, 1.5, n)
    discount = np.clip(rng.normal(.10, .018, n), .07, .16)

    # USD billions. The two commodity-price anchors are rounded published NPVs.
    # The $3/lb scenario also changes the gold price; this proxy does not model gold.
    anchor = 13 + (copper - 4.03) * (9 / 1.03)
    extra_capex = 8.83 * overrun
    future_value = 21.83 * (1.08 / (1 + discount)) ** 11
    delayed_value = future_value / (1 + discount) ** delay
    npv = anchor - extra_capex + operating_shock + delayed_value - 21.83

    return {
        "npv": npv, "copper": copper, "overrun": overrun,
        "delay": delay, "operating_shock": operating_shock,
        "discount": discount,
    }


def summarize(data):
    npv = data["npv"]
    return {
        "draws": len(npv),
        "mean_npv_usd_bn": float(np.mean(npv)),
        "median_npv_usd_bn": float(np.median(npv)),
        "p05_npv_usd_bn": float(np.quantile(npv, .05)),
        "p95_npv_usd_bn": float(np.quantile(npv, .95)),
        "negative_npv_pct": float(100 * np.mean(npv < 0)),
    }


def write_outputs(data, out):
    out.mkdir(parents=True, exist_ok=True)
    summary = summarize(data)
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["measure", "value"])
        writer.writerows(summary.items())

    with (out / "scenarios.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["npv_usd_bn", "copper_usd_lb", "capital_overrun_fraction",
                         "delay_years", "operating_shock_usd_bn", "discount_rate"])
        writer.writerows(zip(data["npv"], data["copper"], data["overrun"],
                             data["delay"], data["operating_shock"], data["discount"]))

    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.hist(data["npv"], bins=65)
    ax.axvline(0, linewidth=2, label="NPV = 0")
    ax.axvline(summary["mean_npv_usd_bn"], linewidth=2, label="Simulated mean")
    ax.set(xlabel="After-tax NPV (USD billions; surrogate)", ylabel="Scenarios",
           title="Reko Diq: 10,000 illustrative scenarios")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "npv_distribution.png", dpi=170)
    plt.close(fig)

    labels = {
        "copper": "Copper price", "overrun": "Capital overrun",
        "delay": "Construction delay", "operating_shock": "Other operating shock",
        "discount": "Discount rate",
    }
    correlations = sorted(
        [(label, spearmanr(data[key], data["npv"]).statistic)
         for key, label in labels.items()], key=lambda item: abs(item[1])
    )
    fig, ax = plt.subplots(figsize=(9, 3.9))
    ax.barh([label for label, _ in correlations], [value for _, value in correlations])
    ax.axvline(0, linewidth=.6)
    ax.set(xlim=(-1, 1), xlabel="Spearman rank correlation with simulated NPV",
           title="Sensitivity (association, not causation)")
    fig.tight_layout()
    fig.savefig(out / "sensitivity.png", dpi=170)
    plt.close(fig)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--draws", type=int, default=DRAWS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    if args.draws < 1:
        parser.error("--draws must be positive")
    summary = write_outputs(simulate(args.draws, args.seed), args.output)
    for name, value in summary.items():
        print(f"{name}: {value:.6f}" if isinstance(value, float) else f"{name}: {value}")


if __name__ == "__main__":
    main()
