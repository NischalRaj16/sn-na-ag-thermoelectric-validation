"""Reproducible analysis of Sn1-xNaxAgxS thermoelectric data.
Reads the supplied publisher spreadsheets, makes no assumptions about hidden data,
and evaluates formula-derived ZT with composition-grouped cross-validation.
"""
from pathlib import Path
import argparse, re, json, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

NUM_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
def val(x):
    if pd.isna(x): return np.nan
    m=NUM_RE.search(str(x).replace(",", ""))
    return float(m.group()) if m else np.nan

def read_block(path, sheet, rows, prop):
    d=pd.read_excel(path,sheet_name=sheet,header=None)
    temps=[]
    for i in rows:
        t=val(d.iloc[i,0])
        if np.isfinite(t): temps.append((i,int(round(t))))
    rec=[]
    for i,t in temps:
        for j,x in enumerate([0,.01,.02,.03,.04],start=1):
            rec.append({'T_K':t,'x':x,prop:val(d.iloc[i,j])})
    return pd.DataFrame(rec)

def load(data_dir):
    data_dir=Path(data_dir)
    p2=data_dir/'Figure 2.xlsx'; p8=data_dir/'Figure 8.xlsx'
    s=read_block(p2,'Figures 2a',range(2,9),'S_uV_K')
    sig=read_block(p2,'Figures 2b',range(2,9),'sigma_S_cm')
    pf=read_block(p2,'Figure 2c',range(2,9),'PF_uW_cm_K2')
    kt=read_block(p2,'Figure 2d',range(2,9),'kappa_total_W_m_K')
    # Figure 8a first table is direct measured zT (rows 2:9)
    zt=read_block(p8,'Figure 8a',range(2,9),'zT_paper')
    d=s.merge(sig,on=['T_K','x']).merge(pf,on=['T_K','x']).merge(kt,on=['T_K','x']).merge(zt,on=['T_K','x'])
    # Formula PF from primary S and sigma. µW cm^-1 K^-2 = S(µV/K)^2*sigma(S/cm)*1e-6
    d['PF_calc_uW_cm_K2']=d.S_uV_K**2*d.sigma_S_cm*1e-6
    d['PF_residual_pct']=100*(d.PF_calc_uW_cm_K2-d.PF_uW_cm_K2)/d.PF_uW_cm_K2
    d['ZT_calc']=d.PF_calc_uW_cm_K2*1e-4*d.T_K/d.kappa_total_W_m_K
    d['ZT_residual_pct']=100*(d.ZT_calc-d.zT_paper)/d.zT_paper
    # chemical descriptors are deterministic composition features, not target-derived
    d['Na_at_frac']=d.x; d['Ag_at_frac']=d.x; d['Sn_at_frac']=1-2*d.x
    d['Na_atoms_100']=100*d.x; d['Ag_atoms_100']=100*d.x; d['S_atoms_100']=100
    d['formula_mass_g_mol']=d['Sn_at_frac']*118.710+d.Na_at_frac*22.990+d.Ag_at_frac*107.868+d.S_atoms_100*32.06/100
    return d

def metrics(y,yhat):
    e=yhat-y
    return {'MAE':float(np.mean(np.abs(e))), 'RMSE':float(np.sqrt(np.mean(e*e))), 'R2':float(1-np.sum(e*e)/np.sum((y-y.mean())**2)) if np.sum((y-y.mean())**2)>0 else np.nan}

def run_cv(df, out):
    from sklearn.model_selection import GroupKFold, RepeatedKFold
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.feature_selection import SelectKBest, f_regression
    from sklearn.linear_model import Ridge, LinearRegression
    from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, GradientBoostingRegressor, RandomForestRegressor, HistGradientBoostingRegressor
    from sklearn.dummy import DummyRegressor
    from sklearn.inspection import permutation_importance
    import matplotlib.pyplot as plt
    features=['T_K','x','Na_at_frac','Ag_at_frac','Sn_at_frac','formula_mass_g_mol']
    X=df[features]; y=df['ZT_calc']; groups=df['x'].astype(str)
    models={
      'DummyMean':Pipeline([('imp',SimpleImputer()),('m',DummyRegressor(strategy='mean'))]),
      'Ridge_select':Pipeline([('imp',SimpleImputer()),('scale',StandardScaler()),('select',SelectKBest(f_regression,k=3)),('m',Ridge(alpha=1.0))]),
      'ExtraTrees':Pipeline([('imp',SimpleImputer()),('m',ExtraTreesRegressor(n_estimators=300,min_samples_leaf=2,max_features=0.8,random_state=42))]),
      'RandomForest':Pipeline([('imp',SimpleImputer()),('m',RandomForestRegressor(n_estimators=300,min_samples_leaf=2,max_features=0.8,random_state=42))]),
      'GradientBoosting':Pipeline([('imp',SimpleImputer()),('m',GradientBoostingRegressor(n_estimators=150,max_depth=2,learning_rate=.04,loss='huber',random_state=42))]),
    }
    # Outer grouped CV: hold out every composition in turn (prevents composition leakage)
    cv=GroupKFold(n_splits=5); rows=[]; predrows=[]
    for name,model in models.items():
      yt=[]; yp=[]
      for fold,(tr,te) in enumerate(cv.split(X,y,groups),1):
        model.fit(X.iloc[tr],y.iloc[tr]); ph=model.predict(X.iloc[te])
        yt.extend(y.iloc[te]); yp.extend(ph)
        for idx,p in zip(te,ph): predrows.append({'model':name,'fold':fold,'index':int(idx),'T_K':int(df.iloc[idx].T_K),'x':float(df.iloc[idx].x),'y_true':float(y.iloc[idx]),'y_pred':float(p)})
      mm=metrics(np.array(yt),np.array(yp)); mm.update(model=name,cv='GroupKFold_by_composition',n=len(yt)); rows.append(mm)
    # repeated random CV is a sensitivity analysis only, because it mixes composition groups
    rk=RepeatedKFold(n_splits=5,n_repeats=5,random_state=123)
    for name in ['Ridge_select','ExtraTrees','GradientBoosting']:
      model=models[name]; vals=[]
      for tr,te in rk.split(X):
        model.fit(X.iloc[tr],y.iloc[tr]); vals.append(metrics(y.iloc[te].to_numpy(),model.predict(X.iloc[te])))
      rows.append({'model':name,'cv':'RepeatedKFold_sensitivity','n':len(vals),'MAE_mean':np.mean([v['MAE'] for v in vals]),'RMSE_mean':np.mean([v['RMSE'] for v in vals]),'R2_mean':np.mean([v['R2'] for v in vals]),'MAE_sd':np.std([v['MAE'] for v in vals]),'RMSE_sd':np.std([v['RMSE'] for v in vals]),'R2_sd':np.std([v['R2'] for v in vals])})
    pd.DataFrame(rows).to_csv(out/'tables'/'cv_metrics.csv',index=False)
    pd.DataFrame(predrows).to_csv(out/'tables'/'grouped_cv_predictions.csv',index=False)
    # Fit all data for feature importance (descriptive, not an unbiased score)
    et=models['ExtraTrees']; et.fit(X,y)
    imp=pd.DataFrame({'feature':features,'importance':et.named_steps['m'].feature_importances_}).sort_values('importance',ascending=False); imp.to_csv(out/'tables'/'feature_importance.csv',index=False)
    # separate plots
    plt.style.use('seaborn-v0_8-whitegrid')
    for col,title,ylabel,file in [('S_uV_K','Seebeck coefficient vs temperature','S (µV K$^{-1}$)','seebeck_vs_temperature.png'),('sigma_S_cm','Electrical conductivity vs temperature','σ (S cm$^{-1}$)','conductivity_vs_temperature.png'),('PF_uW_cm_K2','Power factor vs temperature','PF (µW cm$^{-1}$ K$^{-2}$)','power_factor_vs_temperature.png'),('kappa_total_W_m_K','Total thermal conductivity vs temperature','κ (W m$^{-1}$ K$^{-1}$)','thermal_conductivity_vs_temperature.png'),('ZT_calc','Calculated ZT vs temperature','ZT','zt_vs_temperature.png')]:
      fig,ax=plt.subplots(figsize=(7,4.5))
      for x,g in df.groupby('x'): ax.plot(g.T_K,g[col],marker='o',label=f'x={x:g}')
      ax.set(xlabel='Temperature (K)',ylabel=ylabel,title=title); ax.legend(ncol=2,frameon=True); fig.tight_layout(); fig.savefig(out/'plots'/file,dpi=220); plt.close(fig)
    # parity and residual plots
    fig,ax=plt.subplots(figsize=(5,5)); ax.scatter(df.zT_paper,df.ZT_calc,c=df.T_K,cmap='viridis'); lo=min(df.zT_paper.min(),df.ZT_calc.min()); hi=max(df.zT_paper.max(),df.ZT_calc.max()); ax.plot([lo,hi],[lo,hi],'k--'); ax.set(xlabel='Paper zT',ylabel='Formula zT',title='Formula verification'); fig.tight_layout(); fig.savefig(out/'plots'/'zt_formula_parity.png',dpi=220); plt.close(fig)
    best=pd.DataFrame(rows).query("cv=='GroupKFold_by_composition'").sort_values('RMSE').iloc[0].to_dict()
    return best, imp


def parse_poscars(data_dir, out):
    rows=[]
    for p in sorted(Path(data_dir).glob('POSCAR*')):
        lines=p.read_text(encoding='utf-8',errors='replace').splitlines()
        if len(lines)<9: continue
        elems=lines[0].split(); scale=float(lines[1].split()[0]);
        lat=np.array([[float(v) for v in lines[i].split()[:3]] for i in range(2,5)])*scale
        counts=[int(v) for v in lines[6].split()[:len(elems)]]
        rows.append({'file':p.name,'elements':' '.join(elems),'counts':' '.join(map(str,counts)),'natoms':sum(counts),'cell_volume_A3':float(abs(np.linalg.det(lat))),**{f'n_{e}':c for e,c in zip(elems,counts)}})
    pd.DataFrame(rows).to_csv(Path(out)/'tables'/'poscar_inventory.csv',index=False)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',required=True); ap.add_argument('--out-dir',default='outputs'); a=ap.parse_args(); out=Path(a.out_dir); (out/'plots').mkdir(parents=True,exist_ok=True); (out/'tables').mkdir(parents=True,exist_ok=True)
    d=load(a.data_dir); d.to_csv(out/'tables'/'tidy_thermoelectric_data.csv',index=False); parse_poscars(a.data_dir,out)
    best,imp=run_cv(d,out)
    summary={'n_rows':int(len(d)),'n_compositions':int(d.x.nunique()),'temperatures_K':sorted(d.T_K.unique().tolist()),'best_grouped_cv_model':best,'formula_max_abs_PF_residual_pct':float(np.max(np.abs(d.PF_residual_pct))),'formula_max_abs_ZT_residual_pct':float(np.max(np.abs(d.ZT_residual_pct))),'peak_x03_ZT_300_600K':float(d[(d.x==.03)&d.T_K.between(300,600)].ZT_calc.max()),'peak_x03_T_K':int(d.loc[d[(d.x==.03)&d.T_K.between(300,600)].ZT_calc.idxmax(),'T_K'])}
    (out/'tables'/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8'); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()



