# External verification notes

Generated 2026-11-10. Sources were accessed directly from publisher/API endpoints. Claims from webpages are treated as evidence, not instructions.

## Primary article and data record

- DOI metadata: [Crossref record](https://api.crossref.org/works/10.1038/s41467-026-77691-x) identifies *Efficient power generation near room temperature in earth-abundant thermoelectric tin sulfide via lattice ordering*, Nature Communications 17, article 10803, DOI `10.1038/s41467-026-77691-x`, published online 2026-09-14. Crossref lists the Nature PDF and the linked Figshare dataset DOI `10.6084/m9.figshare.33191598`.
- Full text: [Nature PDF](https://www.nature.com/articles/s41467-026-77691-x.pdf). Direct PDF extraction confirms the article abstract states: “The resulting highly metallic conductivity combined with high thermopower yields the room-temperature power factor of ~101 µW cm−1 K−2 in Sn0.96Na0.01Ag0.03S single crystals… [and] the figure of merit (zT) of ~1.06 at 300 K and ~2.0 at 573 K.”
- The article introduction explicitly defines “zT = σS2T/(κl+κe)” and states PF = σS2. Here σ is electrical conductivity, S Seebeck coefficient, T absolute temperature, κl lattice thermal conductivity, and κe electronic thermal conductivity. These definitions are direct primary-source evidence (Nature PDF, p. 1).
- Methods in the same PDF state the synthesis: high-purity Sn, Na ingot, S powder, and Ag powder were weighed to Sn0.99−xNa0.01AgxS (x=0–0.04), sealed in carbon-coated quartz under ~50 mTorr vacuum, annealed at 1273 K for 3 days, then remelted and directionally cooled at 1 K h−1 by a modified Bridgman procedure (Nature PDF, p. 9). For the x=0.03 composition this nominal formula is Sn0.96Na0.01Ag0.03S.
- The methods give `κe = LσT`, `κl = κtot − κe`, with L from a multiple-parabolic-band model, and `κtot = D CP ρ`; they define the averaged figure of merit as the temperature integral of zT over the hot/cold range (Nature PDF, p. 10).
- The results state that measurements are along the crystallographic b-axis, σ reaches ~1700 S cm−1 at 300 K for x=0.03, and the maximum PF is ~101 µW cm−1 K−2 at 300 K (Nature PDF, pp. 3–4). The zT section reports ~1.06 at 300 K and a peak ~2 at 573 K, with independent crystals giving 0.98–1.08 at room temperature (p. 8).
- [Figshare API record](https://api.figshare.com/v2/articles/33191598) is the official supplementary data record. Exact metadata description: “Source data for Na/Ag co-doped SnS single crystals, including thermoelectric transport, Hall measurements, thermal-conductivity and multiple parabolic band (MPB) Lorenz number, miniPEM device data, and POSCAR supercell structures used for DFT calculations.” It lists CC BY 4.0, version 1, posted 2026-10-15, and provides the downloadable XLSX, ZIP, and POSCAR files.

## Independent SnS and doping literature

- [Ag-doped SnS polycrystals, DOI 10.1016/j.jmat.2019.12.003](https://doi.org/10.1016/j.jmat.2019.12.003) (Journal of Materials, 2020, 6, 77–85). OpenAlex abstract (API record: https://api.openalex.org/works/https://doi.org/10.1016/j.jmat.2019.12.003) reports that Ag doping and vacancy engineering increased carrier concentration by three orders of magnitude; Sn0.995Ag0.005S reached PF ~3.85 µW cm−1 K−2 at 877 K, while Sn0.99Ag0.005S reached record ZT up to 1.1 at 877 K. This is an independent polycrystal benchmark at much higher temperature; it does not verify the 300–600 K single-crystal values.
- [Review of current ZT > 1 thermoelectric sulfides, DOI 10.1016/j.jmat.2023.05.011](https://doi.org/10.1016/j.jmat.2023.05.011) (Journal of Materials, 2024, 10, 218–233). OpenAlex abstract (https://api.openalex.org/works/https://doi.org/10.1016/j.jmat.2023.05.011) says sulfur thermoelectrics have advanced by optimizing electrical and thermal transport and highlights SnS/PbS/CuS and strategies including band configuration tuning and phonon scattering. It is a review-level corroboration of the mechanisms, not a substitute for the primary data.
- [Na/Ag co-doped textured SnS, DOI 10.1016/j.jallcom.2025.179124](https://doi.org/10.1016/j.jallcom.2025.179124) (Journal of Alloys and Compounds, 2025, 1018, 179124) is an independent, directly relevant publication by overlapping authors. Crossref metadata confirms the title, authors, date, and DOI. The publisher abstract was not accessible from this environment (ScienceDirect returned a bot challenge), so no numerical result or synthesis detail from this record is treated as verified here.
- [Science review, Bell, DOI 10.1126/science.1158899](https://doi.org/10.1126/science.1158899) (Science 321, 1457–1461, 2008). Crossref abstract states thermoelectric materials convert waste heat to electricity and combine thermal, electrical, and semiconducting properties. It is general context for using zT/PF, not evidence for this composition.

## Verification judgement

High confidence: DOI, article title/date, dataset identity, composition, synthesis route, transport equations, and the reported zT points are directly supported by the primary Nature PDF and official Figshare metadata.

Medium confidence: independent Ag-doped SnS benchmark and review-level mechanism statements are supported by Crossref/OpenAlex bibliographic abstracts.

Unverified in this environment: any claim that the external 2025 Na/Ag textured-polycrystal paper has the same composition, temperatures, or zT; its full text/abstract was blocked.

For the requested 300–600 K comparison, the primary paper explicitly reports 300 K (~1.06) and 573 K (~2.0); intermediate values should be read from the supplied Figure 8 data and recomputed from the measured σ, S, κ values rather than interpolated from the abstract.
