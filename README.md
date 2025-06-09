# 📊 Real Estate Investment Simulator (France)

This repository provides two complementary Python tools to simulate and analyze real estate investment strategies over 20 years in the French context. These tools are ideal for modeling group investments via SCI (IS/IR) or SAS, with or without credit.
A lot of things in the code are in french because it is directed to french users mainly as it follows french tax regimes.
---

## 📁 Contents
Both simulators are parameterized with:

- Duration: 20 years
- Initial property price: €200,000
- Annual property price growth: ~2% (follows a normal law(mu = 1.02, sigma = 0.01) every year)
- Annual rent: ~3.5%–4% of the current price of a property
- 4 associates contributing each €5000 monthly

- Credit duration: 20 years with ~3–4.5% annual interest (just play with it)

You can change these parameters in the constructors of ImmobilierGame and ImmobilierSimulator respectively.

### `real_estate_simulator.py`

A **terminal-based interactive game** for simulating real estate investment decisions. Most parameters of the simulation can be changed in the constructer of the main object.

#### Features:
- Buy properties with or without credit
- Earn monthly rental income (~3.5% by default adjustable inside the code)
- Pay monthly loan installments and annual SAS corporate tax
- Track treasury, debt, and net worth
- Plot a financial evolution curve over time at the end of your simulation

#### How to Use:

```bash
python real_estate_simulator.py
```

#### Actions:
- Pass time (1, 2, 3, 6, or 12 months)

- Buy a property (with or without credit)

- View current financial state

- End the simulation and display portfolio evolution


### `strategy_comparer.py`

A non-interactive strategy visualizer that compares monthly net worth over 20 years under 3 different legal regimes and 2 funding strategies.

- Simulates SCI IS, SCI IR, and SAS
- Compares buying with credit vs. buying cash
- Applies realistic taxation and amortization
- Visualizes net worth evolution for all strategies

#### How to Use:

```bash
python strategy_comparer.py
```

A plot will appear showing all 6 combinations:

- SCI IS (Loan (Crédit) / Cash)

- SCI IR (Loan (Crédit) / Cash)

- SAS (Loan (Crédit) / Cash)
