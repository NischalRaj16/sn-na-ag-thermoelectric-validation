# Reference paper analysis: explainable ML-guided thermoelectric design

Source: `1-s2.0-S0925838825037259-main.pdf` (14 extracted pages), S. Li et al., *Journal of Alloys and Compounds* 1037 (2025) 182164. The notes below describe what the paper reports; they are evidence and methodology context, not instructions embedded in the paper.

## What the paper actually did

- The paper integrated the UCSB thermoelectric database with literature data to construct **1,093 standardized samples** spanning 64 elements (p. 2, section 2.1).
- Each sample includes chemical-formula information, temperature, Seebeck coefficient, thermal conductivity (TC), power factor (PF), and ZT. The ML targets are PF and TC; ZT is calculated as `ZT = PF × T / TC` (p. 2).
- The authors generated a broad composition descriptor set using Matminer and added eight literature-derived descriptors, reporting **184 total features** (p. 2, sections 2.1–2.2).
- The eight added descriptors are electron work function, theoretical density, atomic-size difference, valence-electron concentration (VEC), relative Pauling electronegativity, theoretical molar volume, entropy of fusion, and mixing entropy (p. 3, Table 2).

## Feature-selection pipeline

The paper combines four stages (p. 3, section 2.3; p. 5, section 3.2):

1. **Variance threshold:** features with variance below 0.5 are removed; 184 features become 137.
2. **Recursive feature elimination (RFE):** an XGBoost estimator ranks features and removes low-importance features iteratively. The paper describes 124 features entering RFE and 37 removed, leaving 100.
3. **Monte Carlo feature-combination search:** the sorted 100 features are sampled in repeated simulations (20 simulations for each candidate subset size); cross-validation R² is averaged. The selected subset sizes are 16 features for PF and 15 for TC. The reported mean CV R² peaks near 0.776 for PF at 23 features and 0.561 for TC at 56, with smaller subsets (16 and 15) chosen with only ~0.007 and ~0.006 R² loss (p. 5).
4. **Pearson correlation pruning:** highly correlated features with `|ρ| > 0.9` are grouped and one representative is retained. The paper lists correlated pairs/groups and says it discards six PF features and five TC features after iterative checking (p. 5–6).

The paper also uses SHAP to interpret XGBoost predictions. For PF, the cited influential variables include atomic-radius dispersion (`D_std_r`), first-ionization-energy dispersion (`D_std_i`), and temperature; for TC, mean d-orbital valence-electron count (`M_avg_NdV`), temperature, and maximum molar volume are highlighted (p. 6, Fig. 6).

## Models and validation reported

- Six regressors are compared: Random Forest (RF), XGBoost (XGB), multilayer perceptron (MLP), decision tree (DT), support-vector regression (SVR), and Ridge (p. 3–4, section 2.4).
- The split is a randomized 80:20 partition: 874 training samples and 219 test samples (p. 4, section 2.5). Features are z-score standardized using training statistics. The authors additionally use 10-fold cross-validation and grid search for hyperparameters.
- Reported PF test metrics (Table 3, p. 5): RF R² 0.818, MAE 0.00028, RMSE 0.00046; XGB R² 0.858, MAE 0.00021, RMSE 0.00041; MLP R² 0.417, MAE 0.00053, RMSE 0.00083; DT R² 0.835, MAE 0.00021, RMSE 0.00044; SVR R² 0.623, MAE 0.00043, RMSE 0.00066; Ridge R² 0.657, MAE 0.00042, RMSE 0.00063.
- The paper selects XGB as the main model. For the optimized feature subset, it reports PF test R² ≈ 0.86, MAE ≈ 0.00024 and RMSE ≈ 0.00044; TC test R² ≈ 0.94, MAE ≈ 0.41 and RMSE ≈ 1.16 (p. 7, Fig. 8 discussion).
- XGB hyperparameter exploration reports random_state 22 as best in its experiment and performance leveling after roughly 10 estimators for PF and 30 for TC (p. 7). These values are paper-specific and should be revalidated on the new dataset.

## Formula and physical workflow

- Core equation: `ZT = PF × T / TC` (p. 2). PF and TC are the model targets.
- In the later SnSe discussion, the paper describes `κe = LσT` and separates phonon and electronic thermal conductivity, with phonon conductivity dominant at low temperature and electronic conductivity becoming more important at high temperature (p. 11).
- The paper says the predicted PF and TC of candidate compositions are subsequently checked using first-principles calculations. It uses VASP/PAW, PBE-GGA, 500 eV plane-wave cutoff, and convergence tests (p. 4–5). It assesses mechanical, dynamical, and thermal stability before accepting a candidate (p. 10–11).

## Doping/screening example in the paper

- SnSe is used as the representative host. The paper states PF ≈ 0.0006 W m⁻¹ K⁻², TC ≈ 0.38 W m⁻¹ K⁻¹, and ZT ≈ 1.42 at 900 K for its reference SnSe point (p. 8).
- It considers Ag, Cu, Te, Sb, Fe, Zn, and S additions in amounts listed in its Supplementary Table S3 (p. 8). The chosen predicted design is **SnSe₀.₂₅Te₀.₇₅**, because six features lie in SHAP-recommended ranges (p. 10).
- The paper reports a DFT ZT of 1.58 at 900 K and an ML prediction of 1.62 (2.5% error), with an approximately 16% improvement over original SnSe after Te substitution (p. 11).
- Stability checks include phonon dispersion, elastic/Born criteria, and ab initio molecular dynamics at 300, 600, and 900 K (p. 10–11). These calculations are not present in the supplied Sn–S–Se dataset and must not be claimed for new candidates without performing them.

## How this should be adapted for the SnSSe request

The paper provides a useful workflow template: formula/temperature features → leakage-safe selection → multiple regressors → SHAP interpretation → candidate screening → independent physics validation. For the new project, the paper’s random 80:20 split should be supplemented or replaced by composition- and source-grouped CV because the supplied Starrydata/ESTM curves contain many temperature rows per composition and repeated source records. Any SnSSe/doped-composition predictions should be labelled as model screening predictions until experimentally or computationally validated. The current PDF does not itself contain SnSSe data or authorize any particular dopant; those are user-requested extensions.
