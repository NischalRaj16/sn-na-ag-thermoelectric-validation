from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

ROOT = Path(r"C:\Users\kraj8\OneDrive\Documents\ChatGPT\The")
REPORTS = ROOT / "reports"
NAVY, LIGHT, PALE, BORDER, GRAY = "1F4E78", "DCE6F1", "F5F7FA", "D9D9D9", "666666"

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); shd = tcPr.find(qn("w:shd"))
    if shd is None: shd = OxmlElement("w:shd"); tcPr.append(shd)
    shd.set(qn("w:fill"), fill)

def border(cell, color=BORDER):
    tcPr = cell._tc.get_or_add_tcPr(); edges = tcPr.first_child_found_in("w:tcBorders")
    if edges is None: edges = OxmlElement("w:tcBorders"); tcPr.append(edges)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = edges.find(qn("w:" + edge))
        if e is None: e = OxmlElement("w:" + edge); edges.append(e)
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6"); e.set(qn("w:space"), "0"); e.set(qn("w:color"), color)

def margins(cell):
    tcPr = cell._tc.get_or_add_tcPr(); m = tcPr.first_child_found_in("w:tcMar")
    if m is None: m = OxmlElement("w:tcMar"); tcPr.append(m)
    for side, value in (("top", 100), ("start", 120), ("bottom", 100), ("end", 120)):
        x = m.find(qn("w:" + side))
        if x is None: x = OxmlElement("w:" + side); m.append(x)
        x.set(qn("w:w"), str(value)); x.set(qn("w:type"), "dxa")

def repeat_header(row):
    p = row._tr.get_or_add_trPr(); x = OxmlElement("w:tblHeader"); x.set(qn("w:val"), "true"); p.append(x)

def table(doc, headers, rows):
    t = doc.add_table(rows=1, cols=len(headers)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = "Table Grid"
    repeat_header(t.rows[0])
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = str(h); shade(c, NAVY); border(c); margins(c)
        for p in c.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs: r.bold = True; r.font.color.rgb = RGBColor(255,255,255); r.font.size = Pt(8.5)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = "" if val is None else str(val); border(cells[i]); margins(cells[i]); cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri % 2 == 1: shade(cells[i], PALE)
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after = Pt(2)
                for r in p.runs: r.font.size = Pt(8.3)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return t

def page_number(p):
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run("Page ")
    fld = OxmlElement("w:fldSimple"); fld.set(qn("w:instr"), "PAGE"); p._p.append(fld)

def setup(title, subtitle):
    d = Document(); s = d.sections[0]
    s.top_margin = Inches(.7); s.bottom_margin = Inches(.65); s.left_margin = Inches(.75); s.right_margin = Inches(.75)
    st = d.styles
    st["Normal"].font.name = "Aptos"; st["Normal"].font.size = Pt(10); st["Normal"].paragraph_format.space_after = Pt(6); st["Normal"].paragraph_format.line_spacing = 1.08
    for name, size in (("Title",23),("Heading 1",16),("Heading 2",12),("Heading 3",10.5)):
        x = st[name]; x.font.name = "Aptos"; x.font.size = Pt(size); x.font.bold = True; x.font.color.rgb = RGBColor(0,0,0)
        x.paragraph_format.space_before = Pt(12 if name != "Title" else 0); x.paragraph_format.space_after = Pt(6)
    hp = s.header.paragraphs[0]; hp.text = title; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in hp.runs: r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string(GRAY)
    page_number(s.footer.paragraphs[0])
    for r in s.footer.paragraphs[0].runs: r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string(GRAY)
    d.add_paragraph(title, style="Title")
    p = d.add_paragraph(); r = p.add_run(subtitle); r.bold = True; r.font.size = Pt(12); r.font.color.rgb = RGBColor.from_string(NAVY)
    p = d.add_paragraph(); p.add_run("Prepared from the supplied papers, source datasets, project code, model outputs and external verification records. ").bold = True; p.add_run("Measured values, formula checks and model extrapolations are labelled separately.")
    return d

def h(d, text, n=1): d.add_heading(text, level=n)
def p(d, text): d.add_paragraph(text)
def bullets(d, items):
    for item in items: d.add_paragraph(item, style="List Bullet")
def figure(d, path, caption, width=6.2):
    if not path.exists(): return
    q = d.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER; q.add_run().add_picture(str(path), width=Inches(width))
    q = d.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER; r = q.add_run(caption); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = RGBColor.from_string(GRAY)
def sources(d, items):
    for label, url in items:
        q = d.add_paragraph(style="List Bullet"); q.add_run(label + " ").bold = True; q.add_run(url)

def build_snna():
    d = setup("Sn Na Ag S Thermoelectric Validation", "Detailed report for Sn0.96Na0.01Ag0.03S")
    plot = ROOT / "project" / "outputs" / "plots"; out = REPORTS / "Sn-Na-Ag-S detailed report.docx"
    h(d,"Executive summary"); p(d,"The supplied Nature Communications paper and Figshare source files were converted into a reproducible validation and modelling workflow. The central result is reproduced from the source data: Sn0.96Na0.01Ag0.03S reaches zT = 1.058 at 300 K and zT = 1.997 at 573 K. The available table ends at 573 K, so there is no direct 600 K measurement. ExtraTrees is the strongest conservative model under composition-grouped validation, but the dataset is too small to support a general discovery claim.")
    table(d,["Item","Result","Interpretation"],[["Target","Sn0.96Na0.01Ag0.03S","x = 0.03 in Sn0.99-xNa0.01AgxS"],["Source rows","35","Five compositions x seven temperatures"],["Measured range","300, 323, 373, 423, 473, 523, 573 K","No 600 K row"],["Formula residuals","PF <= 0.0167%; zT <= 0.0808%","Spreadsheet-rounding level"],["Best grouped-CV model","ExtraTrees: MAE 0.171, RMSE 0.198, R2 0.779","Corrected composition features"],["Peak target zT","1.997 at 573 K","Measured source / formula reconstruction"]])
    h(d,"Scope and evidence boundaries"); p(d,"The papers supply experimental methods, equations, composition labels and reported transport results. The models and candidate interpretations were implemented in the project code. A model estimate is never presented as an exact measurement, and a formula check is not an independent experiment.")
    h(d,"Source paper and doping design"); p(d,"The paper studies substitutional co-doping in Sn0.99-xNa0.01AgxS with x = 0, 0.01, 0.02, 0.03 and 0.04. Na is held at 1 at.% while Ag is varied on the Sn site. The reported interpretation is that Na adjusts carrier concentration and Ag modifies band structure and lattice dynamics, supported by structural and spectroscopic characterization.")
    p(d,"The synthesis route is a modified Bridgman process: high-purity precursors are loaded into carbon-coated quartz under approximately 50 mTorr, annealed at 1273 K for three days, crushed and sieved, remelted, and directionally cooled at about 1 K per hour over roughly 14 days. The paper defines kappa_total = D Cp rho, kappa_e = L sigma T and kappa_l = kappa_total - kappa_e.")
    h(d,"Dataset inventory and what was used"); p(d,"The supplied Figshare record contains figure-level XLSX exports, ZIP archives and POSCAR structures. The modelling table uses the common rectangular tables from Figure 2a-d and Figure 8a: Seebeck coefficient, electrical conductivity, power factor, total thermal conductivity and published zT. The normalized table contains five compositions and seven temperatures, for 35 rows. Central values were parsed from strings containing plus or minus uncertainty; uncertainty text was not used as a feature.")
    table(d,["Input","Used","Reason"],[["Figure 2a Seebeck","Yes","S in microV/K"],["Figure 2b conductivity","Yes","sigma in S/cm"],["Figure 2c power factor","Yes","PF in microW cm-1 K-2"],["Figure 2d thermal conductivity","Yes","kappa_total in W/mK"],["Figure 8a zT","Yes","Target for reproduction"],["POSCAR supercells","Inventory only","Two structures do not represent 35 rows"],["Alternate DSC / uncertainty tables","Kept separate","Not complete composition-by-temperature tables"]])
    h(d,"Formula calculations and unit checks"); p(d,"For workbook units, PF = S^2 sigma x 10^-6 in microW cm-1 K-2. SI zT is zT = PF x 10^-4 x T / kappa_total, with T in kelvin and kappa_total in W m-1 K-1. Across all 35 rows, the maximum relative PF residual is 0.0167% and the maximum zT residual is 0.0808%, consistent with spreadsheet rounding.")
    table(d,["T (K)","S","sigma","PF","kappa total","kappa lattice","source zT","recomputed zT"],[[300,"243.80","1697.47","100.89","2.862","1.890","1.058","1.05755"],[323,"249.17","1508.59","93.66","2.677","1.750","1.130","1.13008"],[373,"266.85","1145.64","81.58","2.248","1.439","1.354","1.35362"],[423,"285.93","892.56","72.97","1.836","1.124","1.681","1.68117"],[473,"298.47","680.49","60.62","1.556","0.951","1.843","1.84275"],[523,"317.18","499.12","50.21","1.330","0.841","1.974","1.97442"],[573,"334.80","359.82","40.33","1.157","0.771","1.997","1.99733"]])
    h(d,"Data errors found and fixes applied"); bullets(d,["Mixed source tables were separated so alternate DSC and uncertainty entries were not merged into the primary table.","PF is in microW cm-1 K-2 while zT requires W m-1 K-2; explicit 10^-6 and 10^-4 conversions were added and checked.","Plus-or-minus strings were parsed to central values, preventing uncertainty text from becoming a second measurement.","The random row split was replaced by GroupKFold by composition to prevent temperature-row leakage.","A chemistry-feature bug was found in the first code version: it set Na_at_frac = x even though Na is fixed at 0.01 in the paper. The code now uses Na_at_frac = 0.01, Ag_at_frac = x and Sn_at_frac = 0.99 - x, then regenerates metrics and plots.","The missing 600 K source row is reported explicitly; no 600 K measurement was invented.","The two POSCAR files are inventoried but not treated as atomistic features for all transport rows."])
    h(d,"Feature engineering and feature selection"); p(d,"The leakage-controlled feature matrix uses temperature, nominal x, fixed Na fraction, Ag fraction, Sn fraction and formula mass. Measured S, sigma, PF, kappa and zT are excluded. Ridge uses SelectKBest with k = 3 inside each training fold. After the chemistry correction, descriptive all-data ExtraTrees importance is temperature 0.520, Ag fraction 0.135, x 0.125, formula mass 0.113, Sn fraction 0.107 and fixed Na fraction 0.000. Correlated composition variables make these predictive attributions rather than causal doping effects.")
    h(d,"Models and cross-validation"); p(d,"The primary evaluation is five-fold GroupKFold by composition, so all seven temperatures from one held-out composition remain unseen. Repeated random K-fold is retained only as a sensitivity analysis. Models tested were a mean baseline, Ridge with in-fold feature selection, Random Forest, Gradient Boosting and ExtraTrees.")
    table(d,["Model","MAE","RMSE","R2","Assessment"],[["Mean baseline","0.392","0.469","-0.245","Reference"],["Ridge + selection","0.236","0.326","0.398","Linear baseline"],["Random Forest","0.231","0.255","0.632","Tree baseline"],["Gradient Boosting","0.225","0.243","0.666","Nonlinear baseline"],["ExtraTrees","0.171","0.198","0.779","Best grouped-CV model"]])
    h(d,"Where the model was right and where it failed"); p(d,"ExtraTrees correctly captured the broad increase of zT with temperature and ranked best under composition-held-out validation. After the chemistry-feature correction, when x = 0.03 was held out it underpredicted all target points: about 0.925 versus 1.058 at 300 K, 1.362 versus 1.681 at 423 K, and 1.648 versus 1.997 at 573 K. Only five composition groups exist; removing one removes the whole target trajectory. Nonlinear transport, correlated composition variables and regression toward the training mean explain the bias. The 573 K point is also near the upper edge of the data and does not support a 600 K measurement claim.")
    h(d,"Training and testing graphs")
    figs=[("seebeck_vs_temperature.png","Measured Seebeck coefficient curves."),("conductivity_vs_temperature.png","Measured electrical conductivity curves."),("power_factor_vs_temperature.png","Measured power factor curves; target PF is about 101 microW cm-1 K-2 near 300 K."),("thermal_conductivity_vs_temperature.png","Measured total thermal conductivity curves."),("zt_vs_temperature.png","Measured and reconstructed zT curves; target peak near 2 at 573 K."),("zt_formula_parity.png","Supplied versus formula-recomputed zT."),("cv_predicted_vs_observed_ExtraTrees.png","ExtraTrees grouped-CV predicted versus observed zT."),("cv_residuals_ExtraTrees.png","ExtraTrees grouped-CV residuals."),("cv_predicted_vs_observed_Ridge_select.png","Ridge grouped-CV parity."),("cv_predicted_vs_observed_RandomForest.png","Random Forest grouped-CV parity."),("cv_predicted_vs_observed_GradientBoosting.png","Gradient Boosting grouped-CV parity.")]
    for f,c in figs: figure(d,plot/f,c)
    h(d,"External verification and papers compared"); p(d,"Crossref, the Nature publisher record and the official Figshare API were used to verify article identity, DOI, dataset provenance, composition, synthesis route, equations and headline zT values. Independent literature was context, not a replacement for the supplied measurements.")
    table(d,["Reference","Contribution","Use"],[["Nature Communications, DOI 10.1038/s41467-026-77691-x","Primary paper, composition, synthesis, equations, zT","Direct validation source"],["Figshare 33191598","Official XLSX, ZIP and POSCAR provenance","Dataset identity"],["Ag-doped SnS, DOI 10.1016/j.jmat.2019.12.003","Independent high-temperature benchmark","Context only"],["Sulfide review, DOI 10.1016/j.jmat.2023.05.011","Band engineering and phonon scattering","Mechanism context"],["Na/Ag textured SnS, DOI 10.1016/j.jallcom.2025.179124","Related publication","No numerical claim; abstract blocked"],["Bell, DOI 10.1126/science.1158899","General thermoelectric context","Background only"]])
    sources(d,[("Primary article","https://doi.org/10.1038/s41467-026-77691-x"),("Figshare record","https://api.figshare.com/v2/articles/33191598"),("Ag-doped SnS benchmark","https://doi.org/10.1016/j.jmat.2019.12.003"),("Sulfide review","https://doi.org/10.1016/j.jmat.2023.05.011"),("Related Na/Ag paper","https://doi.org/10.1016/j.jallcom.2025.179124")])
    h(d,"Advantages and limitations"); h(d,"Advantages",2); bullets(d,["Reproduces PF and zT with sub-0.1% maximum zT residual.","Uses composition-grouped validation to avoid temperature-row leakage.","Separates measured data, formula checks, predictions and POSCAR inventory.","Provides separate plots, normalized tables, diagnostics and runnable code.","Makes the missing 600 K observation explicit."])
    h(d,"Limitations",2); bullets(d,["Five composition groups and 35 rows give large uncertainty.","Figure-level exports retain source rounding.","No new composition is experimentally measured.","POSCAR files are not used as an atomistic feature model.","Feature importance is not causal mechanism evidence.","Values above 573 K would be extrapolations."])
    h(d,"GitHub contents and reproducibility"); p(d,"The validated project is published at https://github.com/NischalRaj16/sn-na-ag-thermoelectric-validation. It contains project/src, normalized data and checks under project/outputs/tables, separate PNG figures under project/outputs/plots, paper and dataset audit notes, and a README. Run from the project folder:")
    q=d.add_paragraph(); r=q.add_run('python src/run_analysis.py --data-dir "C:\\Users\\kraj8\\Dropbox\\Ms thesis\\Research paper\\Datasets\\33191598" --out-dir outputs'); r.font.name='Consolas'; r.font.size=Pt(9)
    h(d,"Conclusion"); p(d,"For Sn0.96Na0.01Ag0.03S, the measured and formula-recomputed result is zT about 1.06 at 300 K and about 2.00 at 573 K. The model captures the broad trend but is biased low for the held-out target because there are too few independent compositions. The defensible result is validated reproduction and transparent small-data modelling, not a new experimental optimum.")
    d.core_properties.title="Sn Na Ag S Thermoelectric Validation"; d.core_properties.author="Codex"; d.save(out); return out

def build_snsse():
    d=setup("SnSSe Thermoelectric Prediction and Doping Screen","Detailed report for Sn S Se compositions and Ag-doped screening")
    plot=ROOT/"sn-s-se-advanced"/"outputs"/"plots"; out=REPORTS/"SnSSe detailed report.docx"
    h(d,"Executive summary"); p(d,"The SnSSe project searched the supplied dataset directory recursively, extracted relevant Sn-S-Se and Co3InSnSSe curves, combined them with the curated ESTM table, built composition descriptors and evaluated multiple regressors under composition-grouped validation. The final table contains 5,255 measured rows from 880 composition groups. ExtraTrees is strongest (grouped-CV R2 0.698, MAE 0.109, RMSE 0.193). No newly generated doped candidate reached predicted ZT >= 1 throughout 300-600 K. This is a model-screening result, not evidence that no material can reach 1.")
    table(d,["Item","Result","Interpretation"],[["Combined data","5,255 rows; 880 groups","4,830 ESTM + 425 Starrydata"],["Best grouped CV","ExtraTrees R2 0.698, MAE 0.109, RMSE 0.193","Composition-grouped"],["Held-out groups","R2 0.745, MAE 0.097, RMSE 0.166","Separate check"],["Highest new candidate max","About 0.819","None >= 1 across 300-600 K"],["Requested target","Sn0.99Ag0.01S0.94Se0.06","Exact measured PF/kappa not found"],["Result type","Model extrapolation","Needs measurement or DFT"]])
    h(d,"Scope and source papers"); p(d,"The reference paper is Li et al., Journal of Alloys and Compounds 1037 (2025) 182164, DOI 10.1016/j.jallcom.2025.182164. It reports 1,093 samples, 184 features, variance filtering, XGBoost recursive elimination, Monte Carlo subset testing, Pearson pruning, six regressors, an 80:20 split and 10-fold CV. It models PF and thermal conductivity, computes ZT = PF x T / TC, then uses SHAP and DFT stability checks for proposed SnSe compositions. The present workflow adopts these principles but uses grouped validation because the supplied curves contain repeated temperatures per composition.")
    p(d,"The reference paper's SnSe0.25Te0.75 example reports ML and DFT values near zT 1.6 at 900 K after mechanical, dynamical and thermal stability checks. Those checks were not performed here and must not be claimed for the SnSSe candidates.")
    h(d,"Dataset scan and parsing"); p(d,"The Datasets directory was scanned recursively. ESTM contributes 4,830 rows and extracted Starrydata contributes 425 rows for Sn-S-Se and Co3InSnSSe. No standalone pure SnSSe composition cell was found. The literal SnSSe string occurs inside Co3InSnSSe, a different quaternary material; it is retained with its provenance and is not labelled pure SnSSe.")
    table(d,["Family","Finding","Treatment"],[["ESTM clean table","4,830 rows","Measured training table"],["Starrydata Sn-S-Se","425 rows","Merged with source and DOI"],["SnSxSe1-x","Includes Se fractions 0.03, 0.06, 0.09, 0.12, 0.20, 0.30, 0.40, 0.50 and 0.80","Measured references"],["Co3InSnSSe","Literal SnSSe text but quaternary","Separate group"],["Exact Ag target","No measured local row","PF/kappa predicted separately"]])
    h(d,"Feature engineering and feature selection"); p(d,"Formula strings were parsed into normalized elemental fractions. Descriptors include temperature, number of elements, mixing entropy, element fractions, weighted/minimum/maximum/range/standard-deviation statistics for atomic mass, atomic number, electronegativity and radius, formula mass, Sn-Se imbalance and S/Se ratio. This is a transparent lightweight analogue of Matminer, not a claim to reproduce Matminer values. Measured PF, kappa and zT are excluded from the ZT descriptor matrix. Ridge uses in-fold SelectKBest; trees use the descriptor set directly. ExtraTrees permutation importance ranks temperature 0.891, Te 0.112, Sb 0.054, Ge 0.054 and Ag 0.053, followed by radius, mass, atomic number and mixing entropy descriptors.")
    h(d,"Models and cross-validation"); p(d,"Models are Ridge with in-fold selection, Random Forest, ExtraTrees and Gradient Boosting. GroupKFold by composition is primary; a separate held-out composition-group split is also reported. This is stricter than a random 80:20 row split because neighboring temperature rows from one curve are dependent.")
    table(d,["Model","Split","R2","MAE","RMSE"],[["Ridge_select","grouped CV","0.259","0.231","0.302"],["RandomForest","grouped CV","0.644","0.117","0.209"],["ExtraTrees","grouped CV","0.698","0.109","0.193"],["GradientBoosting","grouped CV","0.474","0.181","0.254"],["Ridge_select","held-out groups","0.297","0.213","0.276"],["RandomForest","held-out groups","0.719","0.103","0.174"],["ExtraTrees","held-out groups","0.745","0.097","0.166"],["GradientBoosting","held-out groups","0.485","0.173","0.236"]])
    h(d,"Errors found, root causes and fixes"); bullets(d,["Pure SnSSe was separated from Co3InSnSSe; the literal string alone is not enough to identify a binary composition.","Ag on the Sn site is normalized as Sn1-xAgxS0.94Se0.06, so x = 0.03 is Sn0.97Ag0.03S0.94Se0.06; Sn0.99Ag0.03 is not normalized for this substitution.","The exact Sn0.99Ag0.01S0.94Se0.06 measured PF/kappa row was not found, so its outputs are labelled model extrapolations.","Random row leakage was removed with grouped CV and held-out groups.","ZT is recomputed from PF, T and kappa only when units are compatible; direct ZT and PF/kappa outputs are shown separately.","All generated candidates are marked extrapolation_flag = True; no DFT, phonon, phase-stability or experimental checks are implied."])
    h(d,"Measured references and candidate screen"); p(d,"Measured references include SnS0.88Se0.12 (about 1.02 maximum), SnS0.91Se0.09 (about 1.64), SnS0.94Se0.06 (about 1.25) and SnS0.97Se0.03 (about 1.13). These show that zT >= 1 exists in the measured collection. The newly generated doped screen did not produce a candidate >= 1 across 300-600 K; the highest direct candidate maximum was about 0.819.")
    table(d,["Candidate","Min ZT","Mean ZT","Max ZT","All T >= 1?","Status"],[["Sn0.99Ag0.01S0.94Se0.06","0.524","0.686","0.800","No","Model extrapolation"],["Sn1S0.94Se0.06","0.524","0.697","0.819","No","Baseline model"],["Sn0.99Sb0.01S0.94Se0.06","0.514","0.680","0.798","No","Model extrapolation"],["Sn0.99Cu0.01S0.94Se0.06","0.510","0.677","0.807","No","Model extrapolation"],["Sn0.97Ag0.03S0.94Se0.06","0.508","0.664","0.770","No","Model extrapolation"],["Measured SnS0.91Se0.09","-","-","about 1.64","Observed > 1","Measured source"]])
    h(d,"Requested target Sn0.99Ag0.01S0.94Se0.06"); p(d,"The nearest measured baseline is SnS0.94Se0.06: PF = 4.211 mW m-1 K-2 and zT = 0.495 at 300 K, PF = 3.160 and zT = 0.738 at 423 K, and PF = 1.916 and zT = 0.826 at 573 K. Separate ExtraTrees models for PF and kappa were evaluated for the requested Ag-doped formula and combined with zT = PF T / kappa. The following values are model estimates, not exact measurements.")
    table(d,["T (K)","PF (mW/mK2)","kappa (W/mK)","Formula ZT","Direct model ZT","Status"],[[300,"3.742","2.344","0.479","0.524","Model extrapolation"],[350,"3.437","2.088","0.576","0.576","Model extrapolation"],[400,"3.117","1.818","0.686","0.661","Model extrapolation"],[450,"2.779","1.630","0.767","0.703","Model extrapolation"],[500,"2.413","1.450","0.832","0.736","Model extrapolation"],[550,"2.072","1.310","0.870","0.798","Model extrapolation"],[573,"1.909","1.263","0.866","-","Model extrapolation"],[600,"1.805","1.185","0.914","0.800","Model extrapolation"]])
    p(d,"PF decreases with temperature while predicted kappa also decreases. Formula-based ZT rises toward 550-600 K, but 600 K is an edge-of-range extrapolation. Direct ZT and PF/kappa-derived ZT differ because they are separate fits; the disagreement is an uncertainty signal.")
    h(d,"Where the models were right and where they failed"); p(d,"The models captured broad composition and temperature structure, obtained grouped-CV R2 near 0.70 for ExtraTrees, and ranked temperature as the dominant descriptor. They failed as a discovery oracle for new >=1 candidates because candidate descriptors sit outside measured trajectories, sources use different protocols, and the kappa branch is weak (grouped-CV R2 about 0.449). High-temperature errors are amplified by nonlinear carrier activation, bipolar conduction, transitions and thermal-boundary effects. A good parity plot does not guarantee a reliable 600 K endpoint.")
    h(d,"Training and testing graphs")
    figs=[("measured_snsse_curves.png","Measured Sn-S-Se source curves, including high-ZT references."),("ExtraTrees_grouped_cv_parity.png","ExtraTrees grouped-CV parity."),("ExtraTrees_heldout_groups_parity.png","ExtraTrees held-out composition-group parity."),("RandomForest_grouped_cv_parity.png","Random Forest grouped-CV parity."),("RandomForest_heldout_groups_parity.png","Random Forest held-out-group parity."),("GradientBoosting_grouped_cv_parity.png","Gradient Boosting grouped-CV parity."),("GradientBoosting_heldout_groups_parity.png","Gradient Boosting held-out-group parity."),("Ridge_select_grouped_cv_parity.png","Ridge grouped-CV parity."),("Ridge_select_heldout_groups_parity.png","Ridge held-out-group parity."),("feature_importance.png","Permutation feature importance for ExtraTrees."),("candidate_ZT_heatmap.png","Predicted candidate ZT heatmap, 300-600 K."),("ag_series_zt.png","Predicted Ag-series ZT comparison."),("target_ag01_pf_kappa_zt.png","Requested Ag-doped target: PF, kappa and ZT outputs.")]
    for f,c in figs: figure(d,plot/f,c)
    h(d,"Advantages and limitations"); h(d,"Advantages",2); bullets(d,["Uses the full supplied collection and preserves source/DOI provenance.","Uses composition-grouped validation and a held-out group check.","Separates measured references from generated candidates.","Includes separate PF and kappa modelling for the requested target.","Produces reproducible tables, plots and runnable scripts."])
    h(d,"Limitations",2); bullets(d,["No standalone pure SnSSe row was found; Co3InSnSSe is quaternary.","Exact Ag-doped target lacks a measured PF/kappa record.","Candidates lack DFT, phonon, elastic, molecular dynamics and experimental validation.","ESTM and Starrydata have mixed provenance and protocols.","Kappa is weaker than PF, increasing uncertainty in derived ZT.","600 K is an edge-of-range endpoint for relevant curves.","Descriptors cannot encode all defect, band, microstructure and phonon physics."])
    h(d,"Project files and reproducibility"); p(d,"The advanced workflow is in C:\\Users\\kraj8\\OneDrive\\Documents\\ChatGPT\\The\\sn-s-se-advanced. The main script is src\\run_advanced.py; the PF/kappa check is src\\predict_target_pf_kappa.py; tables are in outputs\\tables; plots are in outputs\\plots; and source audit notes are in research_notes\\SnSSe advanced ZT prediction\\reference_paper_analysis.md. Run:")
    q=d.add_paragraph(); r=q.add_run('python src/run_advanced.py --dataset-root "C:\\Users\\kraj8\\Dropbox\\Ms thesis\\Research paper\\Datasets" --out-dir outputs'); r.font.name='Consolas'; r.font.size=Pt(9)
    q=d.add_paragraph(); r=q.add_run('python src/predict_target_pf_kappa.py'); r.font.name='Consolas'; r.font.size=Pt(9)
    p(d,"The published GitHub repository for the earlier validated Sn-Na-Ag-S project is https://github.com/NischalRaj16/sn-na-ag-thermoelectric-validation. The SnSSe extension is stored in the advanced project folder with its scripts, tables and figures; remote publication status should be checked before citing it as a separate repository.")
    h(d,"Comparison references"); table(d,["Reference","Comparison"],[["Li et al., J Alloys Compd 1037 (2025) 182164, DOI 10.1016/j.jallcom.2025.182164","ML workflow, feature selection, SHAP and DFT validation"],["ESTM / DOI 10.1126/science.aax5123","Measured SnS-Se curves"],["Co3InSnSSe / DOI 10.1016/j.ssc.2014.09.006","Quaternary record containing literal SnSSe"],["Nature Communications Sn-Na-Ag-S / DOI 10.1038/s41467-026-77691-x","Separate project comparison for formulas and grouped validation"]])
    sources(d,[("Reference ML paper","https://doi.org/10.1016/j.jallcom.2025.182164"),("Co3InSnSSe source","https://doi.org/10.1016/j.ssc.2014.09.006"),("ESTM-related source","https://doi.org/10.1126/science.aax5123"),("Sn-Na-Ag-S repository","https://github.com/NischalRaj16/sn-na-ag-thermoelectric-validation")])
    h(d,"Conclusion"); p(d,"The collection contains measured SnS-Se compositions above zT = 1, but the feature-only models do not support a new Ag-doped SnSSe claim at or above 1 across 300-600 K. For Sn0.99Ag0.01S0.94Se0.06, the best-supported statement is a model extrapolation with PF roughly 3.74 to 1.81 mW m-1 K-2 and formula-based ZT roughly 0.48 to 0.91 from 300 to 600 K. Experimental transport and independent DFT/phonon/phase-stability checks are required before synthesis.")
    d.core_properties.title="SnSSe Thermoelectric Prediction and Doping Screen"; d.core_properties.author="Codex"; d.save(out); return out

if __name__ == "__main__":
    print(build_snna()); print(build_snsse())
