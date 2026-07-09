# Optimal Execution Simulator (Almgren-Chriss)

## 1. Overview

This project implements the Almgren-Chriss optimal execution framework from scratch: closed-form trade trajectory calculation, a Monte Carlo simulator with antithetic variates for variance reduction, TWAP/VWAP benchmark strategies, and an efficient frontier construction that traces the cost-risk trade-off across risk-aversion levels. The framework is validated against real intraday price and volume data for TSMC (TSM).

## 2. Motivation

Block trading and execution services have become increasingly central to institutional and private banking as the number of market participants grows and volatility rises. Optimal execution — deciding how, not just when, to trade a large position — is one of the core strategies employed by these desks, since naive execution methods leave real cost on the table.

Client risk appetite varies, so a single fixed execution schedule cannot serve every mandate. The Almgren-Chriss framework is well-suited to this problem because it doesn't produce one static answer — it generates a continuous trade-off frontier between expected execution cost and cost variance, parameterized by a single risk-aversion input. This is directly analogous to the efficient frontier in Markowitz portfolio theory, making it an intuitive and defensible framework for aligning an execution schedule to a given risk tolerance.

## 3. Data

Intraday price and volume data for TSM was sourced from Yahoo Finance (`yfinance`) at 5-minute bar resolution, covering regular trading hours only (09:30–16:00 ET; pre/post-market excluded by default). Volume was averaged across several trading days, grouped by time-of-day, to produce a representative intraday volume profile (78 buckets per day) — smoothing out single-day anomalies for use as a VWAP benchmark input. Realized volatility (σ) was estimated from the standard deviation of 5-minute log/percentage returns, scaled to the model's time step (τ) via the square-root-of-time rule. Arrival price (S₀) was taken as the last observed close in the fetched window. Market impact parameters (η, γ) are user-set assumptions, not calibrated from market data (see Limitations).

## 4. Methodology

**Almgren-Chriss trajectory**: the optimal share-holding schedule is computed in closed form as a hyperbolic-sine decay curve, parameterized by an urgency coefficient κ derived from risk-aversion (λ), volatility (σ), and impact parameters (η, γ). As λ → 0, the trajectory converges to a linear (TWAP-like) schedule; larger λ front-loads execution to reduce timing risk.

**Simulation**: realized execution is simulated via a discrete-time random walk for the mid-price, with permanent impact shifting the price path and temporary impact affecting only the execution price of each period's trade. Implementation shortfall (IS) — the dollar gap between arrival price and realized execution — is computed per simulated path.

**Variance reduction**: naive Monte Carlo required a large number of simulations to produce a stable mean cost estimate. Antithetic variates were used: each random shock path is paired with its mirror (negated) path, and the pair's IS values are averaged to estimate the mean with substantially reduced sampling noise. Because this pairing cancels most of the random component (the model is linear in the shocks), variance is instead estimated from the raw, unpaired IS values, preserving the true spread of outcomes.

**Efficient frontier**: λ is swept across a range, and for each value, the AC trajectory and Monte Carlo simulation are re-run to produce a (mean cost, variance of cost) point. The resulting frontier is the execution-cost analog of the Markowitz mean-variance frontier. Note that the λ range must be recalibrated whenever τ, σ, η, or γ change — the same λ value can represent negligible or extreme urgency depending on these other parameters.

**Benchmarks**: TWAP splits shares equally across all periods. VWAP splits shares proportionally to historical average volume per period.

## 5. Results

Almgren-Chriss is benchmarked against TWAP and VWAP in `notebooks/04_comparison.ipynb`, using real TSM intraday price and volume data. Three λ values were selected from distinct regions of the efficient frontier to represent low, moderate, and high risk-aversion.

The execution trajectory plot cleanly illustrates the theoretical prediction: as λ increases, the AC schedule becomes more convex and front-loaded, trading a larger share of the order early to reduce exposure to price risk. At low λ, the trajectory converges toward TWAP's linear schedule, as expected from theory.

The cost comparison shows that AC with λ=0.15 (mild risk-aversion) dominates the TWAP benchmark, achieving both a lower mean cost and lower variance. Higher-λ AC schedules exhibit the expected trade-off — materially higher mean cost in exchange for a substantial reduction in variance — giving a trading desk a genuine menu of options rather than a single fixed schedule.

VWAP underperforms both TWAP and low-λ AC on mean cost, despite concentrating trading volume in the historically most liquid periods of the day. This result is a direct consequence of the model's linear impact assumption: temporary impact cost scales with trade size regardless of how favorable the prevailing liquidity is, so VWAP's larger trades during high-volume windows are penalized rather than rewarded. This is a property of the model, not a general critique of VWAP as a strategy — real-world impact is more commonly modeled as concave (e.g. the square-root law), under which VWAP's behavior of trading more when the market can better absorb it would be expected to perform more favorably.

## 6. Limitations

**Linear impact assumption.** Both temporary and permanent impact are modeled as linear in trade size. This is the standard textbook Almgren-Chriss specification, but it structurally disadvantages volume-seeking strategies like VWAP, which are designed around the empirically-supported assumption that impact is concave in participation rate. Results comparing AC/TWAP against VWAP should be read as a property of this model, not a general statement about strategy performance.

**λ is not portable across parameterizations.** Risk-aversion is a single scalar, but the "urgency" it implies depends on its relationship to σ, η, γ, and τ. A λ value calibrated for one time discretization or volatility regime can be meaningless (either negligible or extreme) under another — λ must be re-tuned any time these other parameters change, rather than treated as a fixed, portable setting.

**Static, non-adaptive execution.** The trajectory is computed once, upfront, and followed regardless of how prices actually evolve during execution. Production systems typically re-optimize the remaining schedule conditional on realized price action — an extension deliberately out of scope here.

**Unvalidated impact parameters.** η and γ are user-set assumptions rather than values calibrated against real market microstructure data, so absolute cost figures should be treated as illustrative rather than production-grade estimates.

**Single-asset, single-day validation.** Results are demonstrated on one ticker (TSM) over a limited date range; performance may not generalize across other assets, liquidity regimes, or longer horizons without re-validation.

## 7. Setup

```bash
git clone https://github.com/benjamincheng18/optimal-execution-simulator.git
cd optimal-execution-simulator

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Launch Jupyter to explore the notebooks:

```bash
jupyter notebook
```

Each notebook uses `%load_ext autoreload` / `%autoreload 2` to pick up changes to `src/` modules without restarting the kernel.

**Project structure**
```
src/                    Production modules
  almgren_chriss.py       Closed-form optimal trajectory
  simulator.py            Monte Carlo simulator with antithetic variates
  benchmarks.py           TWAP / VWAP schedules
  data_loader.py          yfinance price/volume/volatility fetch
  frontier.py             Efficient frontier construction and plotting
notebooks/              Exploration and analysis only, no duplicated function defs
  01_exploration.ipynb
  02_yfinance.ipynb
  03_frontier.ipynb
  04_comparison.ipynb
```