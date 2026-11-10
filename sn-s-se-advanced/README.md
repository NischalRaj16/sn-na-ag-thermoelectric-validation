# Advanced Sn–S–Se thermoelectric screening

This extension uses the full supplied dataset collection to model measured ZT and screen doped Sn–S–Se compositions at 300–600 K. It follows the reference paper's ideas—composition descriptors, feature selection, tree models, grouped cross-validation and interpretable feature importance—while keeping extrapolated candidates separate from measured records.

## Run

```powershell
python -m pip install -r requirements.txt
python src/run_advanced.py --dataset-root "C:\Users\kraj8\Dropbox\Ms thesis\Research paper\Datasets" --out-dir outputs
```

## Main outputs

- `outputs/tables/training_tidy.csv`: ESTM plus extracted Sn–S–Se/Co₃InSnSSe rows and descriptors.
- `outputs/tables/model_metrics.csv`: held-out-group and composition-grouped CV metrics.
- `outputs/tables/permutation_importance.csv`: ExtraTrees feature importance.
- `outputs/tables/candidate_screen.csv`: 300–600 K doped Sn–S–Se predictions, all flagged as extrapolation.
- `outputs/tables/candidate_ranked.csv`: candidate summaries by minimum/mean/maximum predicted ZT.
- `outputs/plots/`: training/test parity, grouped-CV parity, feature importance, measured curves and candidate heatmap.

The current model found no newly generated doped candidate with predicted ZT ≥ 1. Existing measured SnS₀.₈₈Se₀.₁₂–SnS₀.₉₇Se₀.₀₃ references do exceed 1 in the source data. Candidate claims require DFT stability and experimental validation.
