# Sn–Na–Ag–S analysis project

This project reads the supplied Nature Communications figure-source spreadsheets and checks the transport equations, then compares small-data regressors under composition-grouped cross-validation.

## Run

From this folder:

```powershell
python -m pip install -r requirements.txt
python src/run_analysis.py --data-dir "C:\Users\kraj8\Dropbox\Ms thesis\Research paper\Datasets\33191598" --out-dir outputs
```

## Outputs

- `outputs/tables/tidy_thermoelectric_data.csv`: 35 normalized rows (five compositions, seven temperatures), with units in column names.
- `outputs/tables/cv_metrics.csv`: grouped leave-one-composition-out metrics and repeated random-K-fold sensitivity metrics.
- `outputs/tables/grouped_cv_predictions.csv`: every grouped-CV prediction.
- `outputs/tables/feature_importance.csv`: descriptive all-data ExtraTrees importance.
- `outputs/tables/poscar_inventory.csv`: parsed POSCAR element counts and cell volumes.
- `outputs/tables/summary.json`: run summary and formula residuals.
- `outputs/plots/*.png`: separate plots for S, σ, PF, κ, ZT, formula parity, grouped-CV prediction parity and grouped-CV residuals.

The grouped CV is the primary result because random row splitting leaks composition trajectories. With five composition groups, uncertainty remains substantial. POSCAR structures are inventoried but not featurized in this baseline; only two DFT supercells are supplied and they do not span the 35 measured rows.

