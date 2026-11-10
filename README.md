# Sn–Na–Ag–S thermoelectric validation

Reproducible analysis of the supplied Nature Communications paper and Figshare source data for Sn₀.₉₆Na₀.₀₁Ag₀.₀₃S.

The project verifies the transport equations, reconstructs the 300–573 K target-composition data, compares leakage-controlled machine-learning models, and produces separate publication-ready plots.

## Main result

The supplied source data reproduce the paper's central zT values: 1.058 at 300 K and 1.997 at 573 K. ExtraTrees is the best grouped cross-validation baseline (MAE 0.165, RMSE 0.195, R² 0.785). The dataset has no direct 600 K observation.

## Contents

- `project/` — runnable code, normalized data, formula checks, model metrics, POSCAR inventory, and plots.
- `reports/` — detailed research report.
- `research_notes/` — paper/dataset audit and external verification notes.

See [`project/README.md`](project/README.md) for installation and execution instructions.
