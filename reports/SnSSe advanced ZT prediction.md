# Advanced Sn–S–Se ZT prediction and dopant screening

## Executive result

The full supplied dataset collection was searched recursively and the curated ESTM thermoelectric table was combined with the extracted Sn–S–Se and Co₃InSnSSe Starrydata curves. The resulting model table contains 5,255 measured rows and 880 composition groups. ExtraTrees was the strongest tested model under composition-grouped validation (R² 0.698, MAE 0.109, RMSE 0.193); on a held-out composition-group split it achieved R² 0.745, MAE 0.097 and RMSE 0.166.

The model screen covered Sn–S–Se base compositions, Ag/Na/Cu/Sb/Te/Zn/Fe/Co/Ga substitution fractions from 0–10%, Se fractions from 0–100%, and 300–600 K. No newly generated doped candidate reached predicted ZT ≥ 1. The highest candidate maximum was approximately 0.819, and its minimum across 300–600 K was approximately 0.524. This negative result is retained as the result of the requested threshold screen; candidate predictions are extrapolations and are not experimental or DFT evidence.

The source data do contain measured high-ZT references: SnS₀.₈₈Se₀.₁₂, SnS₀.₉₁Se₀.₀₉, SnS₀.₉₄Se₀.₀₆ and SnS₀.₉₇Se₀.₀₃ reach observed maxima of approximately 1.02, 1.64, 1.25 and 1.13, respectively. These references show that ZT ≥ 1 is present in the measured collection, while the current feature-only model does not support claiming a new doped composition above that threshold.

## Reference-paper workflow used

The supplied Journal of Alloys and Compounds paper describes 1,093 samples, 184 generated features, variance-threshold filtering, recursive feature elimination with XGBoost, Monte Carlo feature-subset testing, Pearson correlation pruning, six regressors, 8:2 train/test splitting and 10-fold CV. It uses PF and thermal conductivity as targets and computes ZT = PF × T / TC. Its SHAP analysis is used to interpret model predictions and its proposed compositions are intended for later first-principles validation. This project adopts the transferable parts—composition descriptors, nested feature selection, multiple models, grouped validation and interpretable importance—but does not claim to reproduce Matminer descriptors or DFT stability calculations.

## Dataset and parsing

The script reads `ESTM_Dataset/estm_clean_4830.csv` and the extracted Starrydata curves in the supplied `Datasets` directory. It keeps source, DOI, composition and temperature provenance. Starrydata records are pivoted into PF, thermal conductivity and ZT columns when the same curve family provides them. Composition strings are parsed into elemental fractions and compact descriptors: element fractions, element count, mixing entropy, weighted/minimum/maximum/range/standard-deviation statistics for atomic mass, atomic number, electronegativity and radius, formula mass, Sn–Se imbalance, S/Se ratio and temperature.

## Validation and feature selection

Models are Ridge with in-fold SelectKBest, Random Forest, ExtraTrees and Gradient Boosting. The primary split is GroupKFold by composition, preventing temperatures from the same composition appearing in both training and validation folds. A separate held-out composition-group split is reported. ExtraTrees permutation importance ranks temperature first (0.891), followed by Te fraction (0.112), Sb fraction (0.054), Ge fraction (0.054), Ag fraction (0.053), radius mean, mass mean, atomic-number mean and mixing entropy.

## Candidate screen and formulas

The measured target is ZT. Where PF and κ are available, the consistency relation is ZT = PF × T / κ with PF in W m⁻¹ K⁻², T in K and κ in W m⁻¹ K⁻¹. Candidate rows are generated as normalized Sn–S–Se formulas with one optional dopant substituting Sn. Every candidate is marked `extrapolation_flag=True`. No candidate result should be treated as a synthesis recommendation until composition validity, charge balance, phase stability, phonons, transport coefficients and experimental feasibility are checked.

## Outputs

- `sn-s-se-advanced/src/run_advanced.py` — complete runnable pipeline.
- `sn-s-se-advanced/outputs/tables/training_tidy.csv` — normalized training table and descriptors.
- `sn-s-se-advanced/outputs/tables/model_metrics.csv` — held-out and grouped-CV metrics.
- `sn-s-se-advanced/outputs/tables/permutation_importance.csv` — feature importance.
- `sn-s-se-advanced/outputs/tables/candidate_screen.csv` and `candidate_ranked.csv` — 300–600 K candidate predictions.
- `sn-s-se-advanced/outputs/plots/` — parity plots for every model/split, feature importance, measured Sn–S–Se curves and candidate heatmap.
- `research_notes/SnSSe advanced ZT prediction/advanced_ml.md` — implementation notes and limitations.

Run from `sn-s-se-advanced` with:

```powershell
python -m pip install -r requirements.txt
python src/run_advanced.py --dataset-root "C:\Users\kraj8\Dropbox\Ms thesis\Research paper\Datasets" --out-dir outputs
```

The principal scientific limitation is that the candidate compositions are outside the measured training trajectories. DFT, phonon, thermodynamic and experimental checks are required before any candidate can be considered physically validated.

## Requested Ag-doped target: PF and formula-based ZT

The exact composition Sn₀.₉₉Ag₀.₀₁S₀.₉₄Se₀.₀₆ is not present as a measured row in the supplied local data or in the Crossref search performed for this check. The nearest measured baseline is SnS₀.₉₄Se₀.₀₆, with PF = 0.0042106 W m⁻¹ K⁻² and ZT = 0.495 at 300 K, PF = 0.0031595 W m⁻¹ K⁻² and ZT = 0.738 at 423 K, and PF = 0.0019163 W m⁻¹ K⁻² and ZT = 0.826 at 573 K (ESTM source, DOI 10.1126/science.aax5123).

To answer the PF request, separate ExtraTrees models were fit to the measured PF and κ columns and their outputs were combined with ZT = PF·T/κ. For Sn₀.₉₉Ag₀.₀₁S₀.₉₄Se₀.₀₆, the PF/κ-derived model gives PF = 3.742, 3.437, 3.117, 2.779, 2.413, 2.072, 1.909 and 1.805 mW m⁻¹ K⁻² at 300, 350, 400, 450, 500, 550, 573 and 600 K, respectively. The corresponding formula-based ZT estimates are 0.479, 0.576, 0.686, 0.767, 0.832, 0.870, 0.866 and 0.914. These are model extrapolations, not exact measurements; an exact ZT requires measured PF and κ for this composition. The complete table is `sn-s-se-advanced/outputs/tables/target_ag01_pf_kappa_zt.csv`, and the model-validation metrics are in `pf_kappa_model_metrics.csv`.
