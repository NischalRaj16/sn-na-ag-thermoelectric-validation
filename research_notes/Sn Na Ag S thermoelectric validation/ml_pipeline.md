# ML and formula pipeline notes

## Data read and scope
The supplied directory contains figure-level XLSX exports and two POSCAR structures. This pipeline reads the measured composition/temperature tables in `Figure 2.xlsx` and `Figure 8.xlsx`:

- Seebeck coefficient `S` (µV K⁻¹), Figure 2a
- Electrical conductivity `σ` (S cm⁻¹), Figure 2b
- Power factor (µW cm⁻¹ K⁻²), Figure 2c
- Total thermal conductivity `κ_total` (W m⁻¹ K⁻¹), Figure 2d (first table)
- Published zT, Figure 8a (first table)

The common rectangular dataset has 35 rows (5 compositions x = 0, 0.01, 0.02, 0.03, 0.04; 7 temperatures 300, 323, 373, 423, 473, 523, 573 K). Values containing “±” are parsed as central values; uncertainty columns are not used as predictive features. The later tables in Figure 2d and Figure 8a are supplementary/alternate data and are not silently mixed into the measured table.

## Formula checks
Using S in µV K⁻¹ and σ in S cm⁻¹:

`PF [µW cm⁻¹ K⁻²] = S² σ × 10⁻⁶`.

For SI zT, 1 µW cm⁻¹ K⁻² = 10⁻⁴ W m⁻¹ K⁻², hence:

`ZT = PF[µW cm⁻¹ K⁻²] × 10⁻⁴ × T[K] / κ_total[W m⁻¹ K⁻¹]`.

Across all 35 rows, computed PF agrees with Figure 2c to a maximum absolute relative difference of 0.0167% (rounding). Computed zT agrees with Figure 8a central values to a maximum absolute relative difference of 0.0808% (rounding). This is a direct unit/formula verification, not an independent experiment.

For x = 0.03 (Sn₀.₉₆Na₀.₀₁Ag₀.₀₃S), the calculated/published zT values in 300–600 K are 1.058 (300 K), 1.130 (323 K), 1.354 (373 K), 1.681 (423 K), 1.843 (473 K), 1.974 (523 K), and 1.997 (573 K). The maximum sampled value in the requested interval is 1.997 at 573 K. The paper’s DSC-derived alternate zT curve is a separate table and reaches 1.931 at 523 K and 1.894 at 573 K; it is not used as the primary target because it is not available for every composition.

## Feature design and leakage control
Features are temperature, x, Na and Ag fractions, Sn fraction, and formula mass. x and stoichiometric fractions are deterministic composition descriptors; no measured S, σ, κ, PF, or zT values are used as features. The target is formula-derived zT (equivalent to the paper’s central zT within rounding). Feature importance is descriptive only after fitting all rows.

The primary validation is 5-fold `GroupKFold` grouped by composition x. Therefore every test fold contains an unseen composition and no rows from the same composition appear in training; this avoids the severe leakage that would occur if the seven temperatures from each composition were randomly split. With only five compositions, uncertainty is intrinsically large. Repeated random K-fold is reported only as a sensitivity analysis and should not be interpreted as an independent-composition estimate.

## Models and results
Models: mean baseline, standardized Ridge with in-fold SelectKBest (k=3), ExtraTrees, RandomForest, and GradientBoosting. Primary grouped-CV results (35 held-out rows):

| model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Mean baseline | 0.392 | 0.469 | -0.245 |
| Ridge | 0.235 | 0.288 | 0.531 |
| RandomForest | 0.199 | 0.225 | 0.713 |
| GradientBoosting | 0.194 | 0.209 | 0.751 |
| ExtraTrees | **0.165** | **0.195** | **0.785** |

ExtraTrees is the best primary model. Repeated random K-fold scores are higher because composition groups are mixed; they are retained as sensitivity results in `cv_metrics.csv`. In the all-data descriptive ExtraTrees fit, temperature is the largest feature importance (0.523), followed by Na fraction (0.121), Ag fraction (0.098), x (0.097), formula mass (0.084), and Sn fraction (0.077). Correlated deterministic composition features mean these importances should not be interpreted causally.

## Reproducibility
Run from the project root:

`python src/run_analysis.py --data-dir "C:\\Users\\kraj8\\Dropbox\\Ms thesis\\Research paper\\Datasets\\33191598" --out-dir outputs`

Outputs include `outputs/tables/tidy_thermoelectric_data.csv`, `cv_metrics.csv`, grouped predictions, feature importances, `summary.json`, and separate PNG plots for S, σ, PF, κ, zT and formula parity. Dependencies are listed in `requirements.txt`.

## Limitations
This is a small figure-digitization dataset, not a large independent materials database. It supports interpolation/extrapolation across the five supplied compositions and temperatures only. The POSCAR files are retained for structural reference but are not converted into atomistic descriptors in this baseline because no DFT/structure featurizer was supplied; adding such descriptors would require a declared featurization method and separate validation. No claim of a new experimental result is made.

