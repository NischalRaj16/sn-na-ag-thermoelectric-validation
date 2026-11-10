"""Predict PF and thermal conductivity for the requested Ag-doped Sn-S-Se target.

The target has no measured row in the supplied sources, so the outputs are
model extrapolations. ZT is recomputed from the independently predicted PF and
thermal conductivity using ZT = PF*T/kappa.
"""
from pathlib import Path
import sys
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_advanced as ra  # noqa: E402

TARGET = "Sn0.99Ag0.01S0.94Se0.06"
TEMPERATURES = [300, 350, 400, 450, 500, 550, 573, 600]


def main():
    root = HERE.parent / "outputs"
    tables = root / "tables"
    df = pd.read_csv(tables / "training_tidy.csv")
    ignored = {"composition", "source", "DOI", "group", "ZT", "PF", "kappa", "S_uV_K", "rho"}
    features = [c for c in df.columns if c not in ignored and pd.api.types.is_numeric_dtype(df[c])]
    models = {}
    for target in ("PF", "kappa"):
        q = df.dropna(subset=[target]).copy()
        q = q[q[target] > 0]
        X = q[features].replace([float("inf"), float("-inf")], 0).fillna(0)
        model = ExtraTreesRegressor(
            n_estimators=300, min_samples_leaf=2, max_features=0.9,
            random_state=42, n_jobs=1
        )
        model.fit(X, q[target].astype(float))
        models[target] = model

    rows = []
    for temperature in TEMPERATURES:
        Xnew = pd.DataFrame([ra.comp_features(TARGET, temperature)])[features]
        pf = float(models["PF"].predict(Xnew)[0])
        kappa = float(models["kappa"].predict(Xnew)[0])
        rows.append({
            "composition": TARGET,
            "T_K": temperature,
            "predicted_PF_W_mK2": pf,
            "predicted_PF_mW_mK2": pf * 1000,
            "predicted_kappa_W_mK": kappa,
            "formula_ZT": pf * temperature / kappa,
            "status": "model extrapolation",
        })
    out = pd.DataFrame(rows)
    direct = pd.read_csv(tables / "candidate_screen.csv")
    direct = direct[direct.candidate == TARGET][["T_K", "predicted_ZT"]]
    out = out.merge(direct, on="T_K", how="left")
    out.to_csv(tables / "target_ag01_pf_kappa_zt.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
