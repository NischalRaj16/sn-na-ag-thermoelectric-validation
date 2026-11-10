# Paper and dataset analysis: s41467-026-77691-x

## Scope and source identity

- PDF: `s41467-026-77691-x.pdf`, Nature Communications, article DOI `10.1038/s41467-026-77691-x`, 13 pages in the supplied PDF. The article reports the 2026 study “Efficient power generation near room temperature in earth-abundant thermoelectric tin sulfide via lattice ordering.”
- Dataset folder: `C:\Users\kraj8\Dropbox\Ms thesis\Research paper\Datasets\33191598\`. It contains source spreadsheets for main figures 1–8, supplementary figures, two POSCAR files, and two ZIP archives. `project/data_inventory.json` records every workbook/sheet shape and a short head sample.
- The PDF is treated as source material. Its experimental claims are not instructions; the requested ML/verification workflow is the user’s instruction.

## Page-by-page claims and methods (based on extracted PDF text)

1. **Page 1:** Abstract and background. The material is p-type SnS with Na and Ag substitution. The key composition is `Sn0.96Na0.01Ag0.03S` (the series is `Sn0.99−xNa0.01AgxS`). Reported room-temperature power factor is ~101 µW cm−1 K−2; reported zT is ~1.06 at 300 K and ~2.0 at 573 K. The article defines `zT = σ S² T/(κ_l + κ_e)` and `PF = σ S²`.
2. **Page 2:** Motivation and mechanism. Na+ is first used to regulate hole concentration; Ag+ is introduced as a secondary aliovalent dopant to reconstruct/converge valence bands. Higher Ag creates a modulated multiband configuration. Figure 1 compares x = 0, 0.01, 0.02, 0.03 and 0.04.
3. **Page 3:** Main transport trends. Ag incorporation increases weighted mobility and reduces lattice thermal conductivity. The x = 0.03 sample is the optimized composition; the article states a zT peak near 2. The main text describes single-crystal growth and transport measurements and points to supplementary data.
4. **Page 4:** Structural evidence. Rietveld/SR-PXRD, Sn and Ag XANES/EXAFS, and Raman data support Ag substitution and bond-angle/lattice-dynamical changes. Figure 3 source data contain spectra and fits, not a tabular ML dataset.
5. **Page 5:** EXAFS and Raman interpretation. Ag–S and Sn–S local environments are compared; Ag substitution changes vibrational anisotropy. STEM images show local distortion/dislocation features in x = 0.03.
6. **Page 6:** Electronic structure. ARPES and DFT are compared for Sn70Na1Ag1S72 and Sn69Na1Ag2S72 supercells. The POSCAR files in the dataset correspond to these DFT supercells, not to the macroscopic measured stoichiometry directly.
7. **Page 7:** Band/transport interpretation. The paper connects band modulation to enhanced Seebeck coefficient and mobility; multiband Boltzmann calculations are used. Hall carrier concentration and mobility trends are supplied in the Figure 7 workbook.
8. **Page 8:** Figure of merit and device. The article reports x = 0.03 zT ≈ 1.06 at 300 K, ≈2.0 at 573 K, and average zT ≈1.57 over the reported range. Independent crystals give room-temperature zT values 0.98–1.08 (Supplementary Fig. 30). Cycling is stable through 573 K; TGA shows negligible mass loss in the investigated range. Device data include a 243 K gradient, ~3.3% efficiency and ~0.31 W cm−2 output power density.
9. **Pages 9–10:** Experimental methods. Precursors: Sn pellets 99.99 wt%, Na ingot 99.99 wt%, S powder 99.98 wt%, Ag powder 99.999 wt%. Stoichiometry is calculated for x = 0, 0.01, 0.02, 0.03, 0.04. Precursors are loaded in carbon-coated quartz, sealed at ~50 mTorr under vacuum, annealed to 1273 K with a slow ramp and held 3 days, then cooled. Ingots are crushed/ground/sieved (200 mesh). About 20 g powder is sealed in a 13 mm carbon-coated conical quartz tube; for Bridgman growth it is held at 1273 K for 24 h plus 2 days to melt, then transferred to a 1073 K cold zone at ~1 K h−1 cooling rate. Growth takes ~14 days; crystals are furnace-cooled for 1 day. Transport specimens are ~3×3×10 mm3 for σ and S; thermal specimen ~1 mm thick and 6×6 mm2. Hall uses ±5 T PPMS. Thermal conductivity uses laser flash diffusivity, specific heat and Archimedes density, with `κ_tot = D C_P ρ`; `κ_e = L σ T`; `κ_l = κ_tot − κ_e`.
10. **Pages 10–11 (methods continuation):** Hall equations: `n_H = 1/(e R_H)` and `µ_H = σ R_H`. The paper estimates Lorenz number with a multiple-parabolic-band (MPB) model and uses acoustic-phonon scattering factor r = −1/2. Average zT is the temperature integral `zT_avg = (1/(T_h−T_c)) ∫ zT(T)dT`. Device efficiency equation is given in the paper. These are the formulas to reproduce/verify.
11. **Pages 11–13:** Device fabrication, discussion, references and author information. The source spreadsheets are the numerical source data; the PDF figures are not the only copy of the measurements.

## Doping interpretation

The paper’s “doping” is substitutional aliovalent co-doping on the Sn sublattice: Na+ is introduced at fixed nominal 1 at.% (`Na0.01`) and Ag+ is varied from 0–4 at.% (`Agx`), with Sn fraction reduced to keep the cation sum near 1 (`Sn0.99−xNa0.01AgxS`). The target x = 0.03 therefore has nominal formula `Sn0.96Na0.01Ag0.03S`. The text attributes the improvements to (i) hole/carrier-density regulation by Na+, (ii) Ag+-induced valence-band reconstruction/convergence, (iii) higher DOS effective mass while retaining mobility, and (iv) lower lattice thermal conductivity from structural/vibrational modification. Substitution is supported by XRD/Rietveld, XANES/EXAFS, Raman, elemental mapping and STEM; the numerical source files alone do not establish chemical substitution without these characterization results.

## Dataset inventory and mapping

- `Figure 1.xlsx`: Figure 1b weighted mobility/κ_l versus x and Hall carrier concentration at 300 K; Figure 1c zT versus T for x = 0.03.
- `Figure 2.xlsx`: Figure 2a Seebeck S; 2b electrical conductivity σ and a repeated mobility-style block; 2c PF; 2d total κ, lattice κ and simulated κ for x = 0–0.04 at 300–573 K.
- `Figure 3.xlsx`: bond-angle values, XANES/EXAFS traces, and Raman spectra/fits for x = 0–0.04.
- `Figure 5.xlsx`: ARPES/DFT band-dispersion source data.
- `Figure 6.xlsx`: effective-mass/band-related source data.
- `Figure 7.xlsx`: Pisarenko/transport model data (S, mobility, Hall concentration, sample x).
- `Figure 8.xlsx`: zT table, zT from DSC, device P–I and efficiency–I curves for multiple ΔT values.
- `Supplementary Figure 2/6/10.xlsx`: large structural/Rietveld source tables.
- `Supplementary Figure 7.xlsx`: thermal diffusivity, specific heat and DSC data.
- `Supplementary Figure 8.xlsx`: electronic κ and Lorenz-number model blocks. The Lorenz-number columns load as `0.0` at displayed precision in pandas; do not infer that the physical Lorenz number is exactly zero. Use electronic κ or recompute L from κ_e/(σT) with unit conversion if needed.
- `Supplementary Figure 9.xlsx`: MPB/SPB lattice κ and sensitivity values.
- `Supplementary Figure 11–15.xlsx`: EXAFS/ARPES fitting and effective-mass/Pisarenko data.
- `Supplementary Figure 20–22.xlsx`: Hall/transport and AMSET-related data; 21/22 include README sheets.
- `Supplementary Figures 23–26.zip`: polar-mass source `.dat` files.
- `Supplementary Figure 27.zip`: HTML band-structure files.
- `Supplementary Figure 28.xlsx`: simulated zT versus carrier concentration for 3-band and 4-band models.
- `Supplementary Figure 29.xlsx`: orientation/κ-related comparisons.
- `Supplementary Figure 30.xlsx`: repeat-crystal transport and zT reproducibility.
- `Supplementary Figure 31.xlsx`: heating/cooling stability cycles.
- `Supplementary Figure 32.xlsx`: TGA/heat-flow data.
- `Supplementary Figure 33–36.xlsx`: device benchmark, power/efficiency and load data.
- `POSCAR.Sn70Na1Ag1S72` and `POSCAR.Sn69Na1Ag2S72`: DFT structures used for band calculations.

## Normalized x = 0.03 transport table and formula check

`project/x03_transport_normalized.csv` was generated from Figure 2 and Figure 8 source sheets. Units are explicit. PF in µW cm−1 K−2 is converted to W m−1 K−2 by multiplying by 1e−4 before applying `zT = PF*T/κ_tot`. The recomputation matches the source zT to <0.0005 absolute at every listed point:

| T (K) | S (µV/K) | σ (S/cm) | PF (µW cm−1 K−2) | κtot (W/mK) | κl (W/mK) | source zT | recomputed zT |
|---:|---:|---:|---:|---:|---:|---:|---:|
|300|243.80|1697.47|100.89|2.862|1.890|1.058|1.05755|
|323|249.17|1508.59|93.66|2.677|1.750|1.130|1.13008|
|373|266.85|1145.64|81.58|2.248|1.439|1.354|1.35362|
|423|285.93|892.56|72.97|1.836|1.124|1.681|1.68117|
|473|298.47|680.49|60.62|1.556|0.951|1.843|1.84275|
|523|317.18|499.12|50.21|1.330|0.841|1.974|1.97442|
|573|334.80|359.82|40.33|1.157|0.771|1.997|1.99733|

This directly verifies the requested 300–600 K interval at the available measured temperatures (300, 323, 373, 423, 473, 523, 573 K). The source stops at 573 K; there is no 600 K datapoint in the supplied files.

## Data quality and ML cautions

- The workbooks are figure-source data, not a large independent sample-level dataset. Most rows are temperature/composition points derived from the same small set of crystals. Randomly splitting rows can leak temperature/composition trajectories between train and test and produce over-optimistic scores.
- For ML, use grouped or blocked cross-validation (e.g., leave-one-composition-out and leave-temperature-block-out) and report that the effective sample size is small. Feature selection must be fit inside each training fold.
- Do not treat zT as an independent target while simultaneously supplying PF, κtot and T as features unless the goal is a transparent formula-check model; zT is algebraically determined by them. For predictive modeling, define a target (e.g., zT) and clearly separate measured predictors from derived/leaky predictors.
- Keep unit conversions explicit: σ is S cm−1, S is µV K−1, PF is µW cm−1 K−2, κ is W m−1 K−1, T is K. `σ*S²` in native units requires the 1e−4 factor to obtain W m−1 K−2.
- Figure 8a contains apparent source-entry anomalies for x = 0.02 (`0.876 ± 0.876`, `0.949 ± 0.949`, etc.); verify against Figure 1/other source tables before using these uncertainty values. The central zT values are consistent with PF/κ calculations for x = 0.03.
- The published uncertainty includes propagated measurement errors; source tables often contain central values plus `±` text. Parse central values and uncertainties separately.

## Verification conclusion

The supplied source data reproduce the paper’s headline x = 0.03 zT values and the PF/κ formula over 300–573 K. The composition and doping procedure are explicitly documented in the methods. The dataset is suitable for transparent formula verification and small-data model comparison, but not for claiming a generalizable high-capacity ML model without grouped validation and careful leakage controls.
