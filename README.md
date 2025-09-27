# DSGM Dashboard — Dynamic Stakeholder Graph Model

Open-source dashboard to **simulate and visualize inclusion dynamics** in Internet governance.  
Implements the modeling framework from the paper:

> *Towards Inclusive Internet Governance: A Multidimensional Analysis of Systemic Barriers and Reform Strategies* (IEEE, 2025).

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
<!-- Add Zenodo DOI badge once minted -->
<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXX.svg)](https://doi.org/10.5281/zenodo.XXXX) -->

---

## Table of Contents
- [Features](#features)
- [Repository Layout](#repository-layout)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Docker](#docker)
- [Releases & DOI](#releases--doi)
- [Cite This Work](#cite-this-work)
- [Contributing](#contributing)
- [License](#license)

---

### Features
- **Dynamic Stakeholder Graph Model (DSGM)**
  - \( P_{t+1} = \alpha P_t + \beta S_t - \gamma O_t + \delta \pi_t \)
- **Weighted influence network** of Internet governance stakeholders
- **Time-series simulations** under baseline and policy interventions
- **Metrics (live computation)**
  - Shannon diversity \(H(t)\)
  - Inclusivity Index \(I(t)\)
- **Interactive controls**
  - Adjust α, β, γ, δ, simulation horizon, and policy start
- **Reproducibility**
  - MIT-licensed code
  - Planned DOI via Zenodo
  - Bilingual documentation (EN + FR)

---

## Repository Layout
DSGM-Dashboard/
├── LICENSE.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── .github/workflows/ci-cd.yml
├── docs/
│ ├── index.md # English documentation
│ └── fr/index.md # French documentation
├── notebooks/
│ ├── 01_Static_Simulation.ipynb
│ └── 02_Interactive_Dashboard.ipynb
├── src/
│ └── dsgm/
│ ├── init.py
│ ├── model.py # DSGM simulator + metrics
│ └── dashboard.py # Panel/Bokeh dashboard app
└── data/
└── sample/ # Example datasets

---

## Quick Start

### 1) Create & activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate

### 2) Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

### 3) Run the dashboard
Option A. Module mode (development)
python -m src.dsgm.dashboard

Option B. Panel server mode (deployment)
PYTHONPATH=src panel serve src/dsgm/dashboard.py --autoreload --show

## Usage
- Adjust simulation parameters with the sidebar sliders.
- Explore stakeholder dynamics in real time.
- View Shannon diversity and Inclusivity Index over time.
- Export simulation results as CSV for further analysis.
- Reproduce figures used in the IEEE paper.

## Troubleshooting
- Error: ModuleNotFoundError: No module named 'dsgm'
- Fix: Run with PYTHONPATH=src or install package locally:
pip install -e .

- Error: “Application did not publish any contents.”
- Fix: Ensure template.servable() is placed at module level in dashboard.py.

- Error: macOS LibreSSL warnings
- Fix: Use Python ≥ 3.11 with OpenSSL support.

- Error: Autoreload not working
- Fix: Install watchfiles:
pip install watchfiles

## Docker
- Dockerfile

Copier le code
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install watchfiles
COPY . .
ENV PYTHONPATH=/app/src
EXPOSE 5006
CMD ["panel", "serve", "src/dsgm/dashboard.py", "--address", "0.0.0.0", "--port", "5006", "--allow-websocket-origin", "*"]

Build & run
docker build -t dsgm-dashboard .
docker run --rm -p 5006:5006 dsgm-dashboard

## Releases & DOI
- Create a GitHub Release (e.g., v1.0.0)
- Connect GitHub repo to Zenodo → auto DOI minted
- Add the Zenodo badge above

## Cite This Work
If you use this dashboard, please cite:

@misc{DSGM2025,
  author       = {Karim Attoumani Mohamed},
  title        = {{DSGM-Dashboard}: Dynamic Stakeholder Graph Model},
  year         = {2025},
  howpublished = {GitHub repository},
  note         = {[Online]. Available: https://github.com/KarimAttoumaniMohamed/DSGM-Dashboard}
}

## Contributing
Contributions are welcome:

- Fix bugs or add features (via pull requests)
- Extend to new dimensions (gender, age, disability)
- Add datasets or regional scenarios

## License
MIT License — see LICENSE.md.

Maintainer
Karim ATTOUMANI MOHAMED
Doctoral Researcher — Inclusive Internet Governance
📧 attoukarim@gmail.com   🌐 LinkedIn: https://www.linkedin.com/in/karimattoumanimohamed/

