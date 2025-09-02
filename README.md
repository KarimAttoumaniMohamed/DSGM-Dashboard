# DSGM Dashboard – Dynamic Stakeholder Graph Model

Open-source dashboard to simulate inclusion dynamics in Internet governance, companion to the IEEE paper:
*Towards Inclusive Internet Governance: A Multidimensional Analysis of Systemic Barriers and Reform Strategies* (2025).

## Features
- Weighted influence network visualization
- Time-series participation simulations (baseline / moderate / aggressive)
- Inclusivity index validation vs. empirical data
- Shannon diversity vs. governance resilience

## Quickstart
```bash
python -m pip install -r requirements.txt
python src/dsgm/dashboard.py


---

# 7) Docs (EN/FR)
```bash
cat > docs/index.md << 'EOF'
# DSGM Dashboard (EN)
- Run `python src/dsgm/dashboard.py` to launch the interactive app (Panel + Bokeh).
- Import your CSV/JSON data into `data/` and select via the UI (coming soon).
