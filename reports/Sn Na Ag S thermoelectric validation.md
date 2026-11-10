# Validating doped tin sulfide thermoelectrics

The supplied paper and figure-source files support the requested Sn₀.₉₆Na₀.₀₁Ag₀.₀₃S result: **the published central zT rises from 1.058 at 300 K to 1.997 at 573 K**, and recomputation from the supplied Seebeck, conductivity and thermal-conductivity data reproduces those values with a maximum relative difference of 0.0808%. The available source stops at 573 K, so the requested “300–600 K” comparison contains no 600 K measurement. A leakage-controlled model comparison also identifies ExtraTrees as the strongest baseline (**grouped-CV MAE 0.165, RMSE 0.195, R² 0.785**), but the five-composition figure-derived dataset is too small to support a general materials-discovery claim. The project now contains the parsed data, formula checks, POSCAR inventory, reproducible training script, tables, and separate plots. Direct Nature, Crossref and Figshare records independently verify the article identity, dataset provenance, equations, synthesis route and headline zT values, while independent SnS literature provides medium-confidence context for Ag doping and band/phonon engineering.

## The paper defines a substitutional co-doping experiment

The article identifies the optimized composition as **Sn₀.₉₆Na₀.₀₁Ag₀.₀₃S** within the nominal series Sn₀.₉₉₋ₓNa₀.₀₁AgₓS, with x = 0, 0.01, 0.02, 0.03 and 0.04. Its reported mechanism is a fixed 1 at.% Na substitution to regulate holes, followed by variable Ag substitution to modify the valence-band structure and lattice dynamics. The paper connects Ag incorporation with band convergence, higher effective density of states, retained mobility and reduced lattice thermal conductivity; these are source claims from the supplied 13-page PDF, not instructions embedded in the document ([Nature Communications article DOI](https://doi.org/10.1038/s41467-026-77691-x)).

The experimental method is a bulk single-crystal route. High-purity Sn, Na, S and Ag precursors are weighed for the target stoichiometry, loaded into carbon-coated quartz, sealed at approximately 50 mTorr, annealed to 1273 K for three days, crushed and sieved, then remelted in a carbon-coated conical quartz tube. Bridgman growth proceeds from 1273 K toward a 1073 K cold zone at approximately 1 K h⁻¹ over about 14 days. The paper reports transport specimens of roughly 3 × 3 × 10 mm³ for electrical and Seebeck measurements and a roughly 1 mm thick, 6 × 6 mm² specimen for thermal measurements. It defines κtot = DCPρ, κe = LσT and κl = κtot − κe, with Hall relations nH = 1/(eRH) and μH = σRH. These method details are recorded from the PDF text extraction in [paper_dataset_analysis.md](C:/Users/kraj8/OneDrive/Documents/ChatGPT/The/research_notes/Sn%20Na%20Ag%20S%20thermoelectric%20validation/paper_dataset_analysis.md).

The source files also include two POSCAR structures used for electronic-structure calculations, Sn70Na1Ag1S72 and Sn69Na1Ag2S72. They are DFT supercells for the band calculations, not direct representations of the macroscopic Sn₀.₉₆Na₀.₀₁Ag₀.₀₃S transport specimen. The project parses their element counts and cell volumes into `outputs/tables/poscar_inventory.csv`, while leaving them out of the baseline ML features because two structures cannot represent all 35 measured transport rows.

## The supplied workbooks reproduce the headline transport values

The dataset directory contains figure-level XLSX exports for the main and supplementary figures, two POSCAR files and two ZIP archives. The analysis uses the common, rectangular transport tables from Figure 2a–d and Figure 8a: Seebeck coefficient S, electrical conductivity σ, power factor PF, total thermal conductivity κtot and published zT. The primary normalized table has **35 rows: five compositions × seven temperatures** at 300, 323, 373, 423, 473, 523 and 573 K. Values written as “central ± uncertainty” are parsed into central values for modeling; uncertainty text is retained conceptually but is not used as a feature. A complete workbook/sheet inventory is in [data_inventory.json](C:/Users/kraj8/OneDrive/Documents/ChatGPT/The/project/data_inventory.json).

For native workbook units, the verified equations are

`PF [µW cm⁻¹ K⁻²] = S² [µV² K⁻²] × σ [S cm⁻¹] × 10⁻⁶`

and

`zT = PF [µW cm⁻¹ K⁻²] × 10⁻⁴ × T [K] / κtot [W m⁻¹ K⁻¹]`.

The first conversion follows from converting µW cm⁻¹ to W m⁻¹; the second applies the same 10⁻⁴ factor before using the SI zT definition. Across all 35 rows, calculated PF differs from Figure 2c by at most 0.0167% relative error, and calculated zT differs from Figure 8a by at most 0.0808%, consistent with spreadsheet rounding. This validates the formulas and unit handling against the source data; it is not an independent experimental replication.

For the target composition, the normalized values are:

| T (K) | S (µV/K) | σ (S/cm) | PF (µW cm⁻¹ K⁻²) | κtot (W/mK) | κl (W/mK) | source zT | recomputed zT |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 300 | 243.80 | 1697.47 | 100.89 | 2.862 | 1.890 | 1.058 | 1.05755 |
| 323 | 249.17 | 1508.59 | 93.66 | 2.677 | 1.750 | 1.130 | 1.13008 |
| 373 | 266.85 | 1145.64 | 81.58 | 2.248 | 1.439 | 1.354 | 1.35362 |
| 423 | 285.93 | 892.56 | 72.97 | 1.836 | 1.124 | 1.681 | 1.68117 |
| 473 | 298.47 | 680.49 | 60.62 | 1.556 | 0.951 | 1.843 | 1.84275 |
| 523 | 317.18 | 499.12 | 50.21 | 1.330 | 0.841 | 1.974 | 1.97442 |
| 573 | 334.80 | 359.82 | 40.33 | 1.157 | 0.771 | 1.997 | 1.99733 |

The paper’s alternate DSC-derived zT curve is kept separate because it is not a complete composition-by-temperature table; it reaches about 1.931 at 523 K and 1.894 at 573 K. It should not be silently mixed with the primary Figure 8a target. Figure 8 also contains apparent duplicated uncertainty entries for x = 0.02; those uncertainty values are flagged for review rather than treated as physical measurements.

## Grouped validation changes the interpretation of model quality

The ML target is zT, which is algebraically derived from PF, temperature and κtot. To prevent trivial leakage, the feature matrix contains only temperature, nominal composition fractions, x and formula mass; measured S, σ, PF, κtot and zT are excluded. Feature selection is performed inside each training fold for the Ridge model using SelectKBest(k = 3). The primary validation is five-fold GroupKFold by composition, so all seven temperatures from a held-out composition remain unseen during training. This is the appropriate conservative test for the supplied data because a random row split would place neighboring temperatures from the same composition in both train and test sets.

The held-out results are:

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Mean baseline | 0.392 | 0.469 | −0.245 |
| Ridge + in-fold feature selection | 0.235 | 0.288 | 0.531 |
| RandomForest | 0.199 | 0.225 | 0.713 |
| GradientBoosting | 0.194 | 0.209 | 0.751 |
| **ExtraTrees** | **0.165** | **0.195** | **0.785** |

ExtraTrees is the best primary model, but the score must be read with the small number of groups in mind: only five composition groups exist, so one composition determines each test fold and uncertainty is substantial. Repeated random K-fold results are retained as sensitivity analysis only; they are higher because composition trajectories are mixed between training and testing. In the descriptive all-data ExtraTrees fit, temperature has the largest importance (0.523), followed by Na fraction (0.121), Ag fraction (0.098), x (0.097), formula mass (0.084) and Sn fraction (0.077). Because these composition variables are deterministic and correlated, importance is predictive attribution, not a causal doping effect.

The model and formula checks are implemented in [run_analysis.py](C:/Users/kraj8/OneDrive/Documents/ChatGPT/The/project/src/run_analysis.py). The generated tables include normalized data, grouped predictions, metrics, feature importance, POSCAR inventory and a JSON summary. Separate plots are saved for Seebeck coefficient, conductivity, power factor, thermal conductivity, zT, formula parity, model prediction parity and model residuals in [project/outputs/plots](C:/Users/kraj8/OneDrive/Documents/ChatGPT/The/project/outputs/plots). The full workflow and dependency list are documented in [README.md](C:/Users/kraj8/OneDrive/Documents/ChatGPT/The/project/README.md).

## What the dataset can and cannot establish

The workflow establishes internal consistency: the supplied source spreadsheets reproduce the target composition’s zT curve, the formulas and unit conversions are correct, and grouped validation produces a transparent model ranking. It does not establish a new material result, prove substitution chemistry from spreadsheets alone, or demonstrate a high-capacity generalizable predictor. Chemical substitution is supported in the paper by XRD/Rietveld, XANES/EXAFS, Raman, STEM and elemental mapping; the numerical workbooks alone cannot reproduce those characterization conclusions.

External verification now supports the primary evidence. Crossref identifies the paper as *Efficient power generation near room temperature in earth-abundant thermoelectric tin sulfide via lattice ordering* (Nature Communications 17, article 10803, published 2026-09-14) and links the official Figshare record ([Crossref](https://api.crossref.org/works/10.1038/s41467-026-77691-x); [Nature PDF](https://www.nature.com/articles/s41467-026-77691-x.pdf); [Figshare API](https://api.figshare.com/v2/articles/33191598)). The publisher PDF directly supports the composition, PF ≈101 µW cm⁻¹ K⁻² at 300 K, zT ≈1.06 at 300 K, zT ≈2.0 at 573 K, the zT/PF definitions, and the 1273 K modified-Bridgman synthesis. Figshare metadata independently identifies the supplied XLSX, ZIP and POSCAR files as source data for Na/Ag co-doped SnS transport, Hall, thermal, MPB Lorenz and DFT calculations.

Independent literature provides context but does not replace the primary measurement. Ag-doped SnS polycrystals reported PF ≈3.85 µW cm⁻¹ K⁻² and ZT up to ≈1.1 at 877 K ([Journal of Materials, 2020](https://doi.org/10.1016/j.jmat.2019.12.003); [OpenAlex record](https://api.openalex.org/works/https://doi.org/10.1016/j.jmat.2019.12.003)), and a 2024 review summarizes band-configuration tuning and phonon scattering as established sulfide optimization strategies ([Journal of Materials review](https://doi.org/10.1016/j.jmat.2023.05.011)). These are medium-confidence, higher-temperature or review-level comparisons and do not independently reproduce the 300–573 K single-crystal curve. The 2025 Na/Ag textured-SnS publication is bibliographically verified ([Crossref DOI](https://doi.org/10.1016/j.jallcom.2025.179124)), but its abstract was blocked in this environment, so no numerical claim from it is used.

## Reproduce the project from the supplied files

From [C:/Users/kraj8/OneDrive/Documents/ChatGPT/The/project](C:/Users/kraj8/OneDrive/Documents/ChatGPT/The/project), install the packages in `requirements.txt` and run:

```powershell
python -m pip install -r requirements.txt
python src/run_analysis.py --data-dir "C:\Users\kraj8\Dropbox\Ms thesis\Research paper\Datasets\33191598" --out-dir outputs
```

The source PDF is [s41467-026-77691-x.pdf](C:/Users/kraj8/Dropbox/Ms%20thesis/Research%20paper/s41467-026-77691-x.pdf). The normalized target table is [x03_transport_normalized.csv](C:/Users/kraj8/OneDrive/Documents/ChatGPT/The/project/x03_transport_normalized.csv), and the formula/model diagnostics are in [outputs/tables](C:/Users/kraj8/OneDrive/Documents/ChatGPT/The/project/outputs/tables). The generated figures are intentionally separate files so each property and validation diagnostic can be inspected independently.

## Conclusion

The material and data check pass: **Sn₀.₉₆Na₀.₀₁Ag₀.₀₃S reaches zT ≈ 2.0 at the highest supplied temperature, 573 K, and the source equations reproduce it to rounding precision**. ExtraTrees is the strongest conservative baseline, while the grouped-CV design prevents the inflated confidence that would result from random temperature-row splitting.

The correct scientific interpretation is a validated reproduction and small-data modeling workflow, not a claim of a newly discovered optimum. The next high-value step is independent web/literature corroboration and, if more measured compositions or structures become available, a blocked evaluation that can test whether the learned trend transfers beyond this single paper’s five-composition series.

