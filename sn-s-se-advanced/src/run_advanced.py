"""Advanced Sn-S-Se thermoelectric screening.

The workflow is intentionally conservative: it predicts measured ZT from
composition/temperature descriptors, evaluates composition-grouped CV, and
labels candidate compositions as model extrapolations. It does not claim an
experimental or DFT validation.
"""
from __future__ import annotations
import argparse, csv, io, json, math, re, zipfile
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.inspection import permutation_importance

ELEMENTS = ['Ag','As','Bi','Br','C','Cd','Co','Cu','Fe','Ga','Ge','In','Na','S','Sb','Se','Sn','Te','Tl','Zn']
AW={'Ag':107.868,'As':74.922,'Bi':208.98,'Br':79.904,'C':12.011,'Cd':112.414,'Co':58.933,'Cu':63.546,'Fe':55.845,'Ga':69.723,'Ge':72.630,'In':114.818,'Na':22.990,'S':32.06,'Sb':121.760,'Se':78.971,'Sn':118.710,'Te':127.60,'Tl':204.383,'Zn':65.38}
Z={'Ag':47,'As':33,'Bi':83,'Br':35,'C':6,'Cd':48,'Co':27,'Cu':29,'Fe':26,'Ga':31,'Ge':32,'In':49,'Na':11,'S':16,'Sb':51,'Se':34,'Sn':50,'Te':52,'Tl':81,'Zn':30}
EN={'Ag':1.93,'As':2.18,'Bi':2.02,'Br':2.96,'C':2.55,'Cd':1.69,'Co':1.88,'Cu':1.90,'Fe':1.83,'Ga':1.81,'Ge':2.01,'In':1.78,'Na':0.93,'S':2.58,'Sb':2.05,'Se':2.55,'Sn':1.96,'Te':2.10,'Tl':1.62,'Zn':1.65}
RAD={'Ag':1.45,'As':1.15,'Bi':1.60,'Br':1.14,'C':0.70,'Cd':1.44,'Co':1.25,'Cu':1.28,'Fe':1.26,'Ga':1.30,'Ge':1.25,'In':1.55,'Na':1.66,'S':1.05,'Sb':1.45,'Se':1.15,'Sn':1.45,'Te':1.40,'Tl':1.70,'Zn':1.34}

def parse_formula(s):
    """Parse simple formula strings and parenthesized strings approximately."""
    s=str(s).replace('(','').replace(')','').replace('[','').replace(']','')
    # Strip leading mixture coefficients and retain element-number tokens.
    toks=re.findall(r'([A-Z][a-z]?)([0-9]*\.?[0-9]*)',s)
    d=Counter()
    for e,n in toks:
        if e in AW: d[e]+=float(n) if n else 1.0
    total=sum(d.values())
    return {e:v/total for e,v in d.items()} if total else {}

def comp_features(formula, T):
    f=parse_formula(formula); vals=np.array(list(f.values()),float)
    def stat(tab):
        if not f:
            return [0.0,0.0,0.0,0.0,0.0]
        x=np.array([tab[e] for e in f],float); w=vals
        return [float(np.sum(w*x)),float(np.min(x)),float(np.max(x)),float(np.max(x)-np.min(x)),float(np.sqrt(np.sum(w*(x-np.sum(w*x))**2)))]
    out={'T':float(T),'n_elements':len(f),'mix_entropy':float(-np.sum(vals[vals>0]*np.log(vals[vals>0]))) if len(f) else 0.0}
    for e in ELEMENTS: out[f'frac_{e}']=f.get(e,0.0)
    for name,tab in [('mass',AW),('Z',Z),('EN',EN),('radius',RAD)]:
        a=stat(tab); out.update({f'{name}_{k}':v for k,v in zip(['mean','min','max','range','std'],a)})
    out['formula_mass']=sum(f[e]*AW[e] for e in f)*max(1,len(f))
    out['Sn_minus_Se']=f.get('Sn',0)-f.get('Se',0)
    out['S_to_Se']=f.get('S',0)/(f.get('Se',0)+1e-9)
    return out

def extract_starry(dataset_root, out_csv):
    """Read only Sn-S-Se/Co3InSnSSe rows from the raw Starrydata curves."""
    curve_dir=Path(dataset_root)/'starrydata2_raw'/'starrydata2_raw'/'curves'
    if not curve_dir.exists(): curve_dir=Path(dataset_root)/'starrydata2_raw'/'curves'
    files={'zt':'starrydata2_20250501_zt.csv','pf':'starrydata2_20250501_power_factor.csv','rho':'starrydata2_20250501_resistivity.csv','S':'starrydata2_20250501_seebeck.csv','kappa':'starrydata2_20250501_thermal_conductivity.csv'}
    rows=[]
    pat=re.compile(r'(?i)(SnS(?:[0-9.]+)?Se(?:[0-9.]+)?|Co3InSnSSe)')
    for prop,fn in files.items():
        p=curve_dir/fn
        if not p.exists(): continue
        with p.open(encoding='utf-8',errors='ignore',newline='') as h:
            rd=csv.DictReader(h)
            for r in rd:
                comp=r.get('composition','')
                if pat.search(comp):
                    rows.append({'SID':r.get('SID'),'composition':comp,'DOI':r.get('DOI'),'T':float(r['Temperature']),'property':prop,'value':float(r['tepvalue']),'unit':r.get('unit_y','')})
    out=pd.DataFrame(rows); out.to_csv(out_csv,index=False); return out

def load_training(dataset_root, outdir):
    estm=Path(dataset_root)/'ESTM_Dataset'/'estm_clean_4830.csv'
    e=pd.read_csv(estm)
    # Use the curated ESTM thermoelectric collection as the broad training set.
    # Sn-S-Se rows remain explicitly identifiable in the saved table and are
    # used as a focused validation slice; broad training reduces extrapolation
    # from only a few chalcogenide families.
    e=e.rename(columns={'formula':'composition','T':'T','pf':'PF','kappa':'kappa','zt':'ZT'})
    e['source']='ESTM'; e['DOI']=e.get('doi','')
    s=extract_starry(dataset_root, outdir/'starry_snsse_long.csv')
    if len(s):
        wide=s.pivot_table(index=['SID','composition','DOI','T'],columns='property',values='value',aggfunc='mean').reset_index()
        wide=wide.rename(columns={'zt':'ZT','pf':'PF','kappa':'kappa','S':'S_uV_K','rho':'rho'})
        # Starry PF is W m-1 K-2; ESTM PF is W m-1 K-2. Keep common units.
        wide['source']='Starrydata';
        for c in ['PF','kappa','ZT']:
            if c not in wide: wide[c]=np.nan
        s2=wide[['composition','T','PF','kappa','ZT','source','DOI']]
        e=e[['composition','T','PF','kappa','ZT','source','DOI']]
        allx=pd.concat([e,s2],ignore_index=True)
    else: allx=e[['composition','T','PF','kappa','ZT','source','DOI']]
    allx=allx.dropna(subset=['ZT','T','composition']).copy()
    # Explicit grouped key prevents temperature duplicates from leaking across folds.
    allx['group']=allx['composition'].astype(str).str.replace(r'\s+','',regex=True)
    feat=pd.DataFrame([comp_features(c,t) for c,t in zip(allx['composition'],allx['T'])]).drop(columns=['T'])
    allx=pd.concat([allx.reset_index(drop=True),feat],axis=1)
    allx.to_csv(outdir/'training_tidy.csv',index=False)
    return allx

def evaluate_models(df, outdir):
    target='ZT'; drop={'composition','source','DOI','group','ZT','PF','kappa','S_uV_K','rho'}
    cols=[c for c in df.columns if c not in drop and pd.api.types.is_numeric_dtype(df[c])]
    X=df[cols].replace([np.inf,-np.inf],np.nan).fillna(0); y=df[target].astype(float); groups=df.group
    gss=GroupShuffleSplit(n_splits=1,test_size=0.2,random_state=42); tr,te=next(gss.split(X,y,groups))
    models={
      'Ridge_select':Pipeline([('scale',StandardScaler()),('select',SelectKBest(f_regression,k=min(12,X.shape[1]))),('model',Ridge(alpha=10))]),
      'RandomForest':RandomForestRegressor(n_estimators=180,min_samples_leaf=2,max_features=0.7,random_state=42,n_jobs=1),
      'ExtraTrees':ExtraTreesRegressor(n_estimators=220,min_samples_leaf=2,max_features=0.9,random_state=42,n_jobs=1),
      'GradientBoosting':GradientBoostingRegressor(n_estimators=250,max_depth=2,learning_rate=0.03,loss='huber',random_state=42)
    }
    metrics=[]; preds=[]
    cv=GroupKFold(n_splits=min(5,groups.nunique()))
    for name,m in models.items():
        m.fit(X.iloc[tr],y.iloc[tr]); p=m.predict(X.iloc[te]);
        metrics.append({'model':name,'split':'heldout_groups','R2':r2_score(y.iloc[te],p),'MAE':mean_absolute_error(y.iloc[te],p),'RMSE':mean_squared_error(y.iloc[te],p)**0.5})
        for idx,val in zip(te,p): preds.append({'model':name,'split':'heldout_groups','index':int(idx),'observed':float(y.iloc[idx]),'predicted':float(val),'composition':df.iloc[idx].composition,'T':float(df.iloc[idx]['T'])})
        pv=np.full(len(y),np.nan)
        for a,b in cv.split(X,y,groups):
            mm=models[name]; mm.fit(X.iloc[a],y.iloc[a]); pv[b]=mm.predict(X.iloc[b])
        metrics.append({'model':name,'split':'grouped_cv','R2':r2_score(y,pv),'MAE':mean_absolute_error(y,pv),'RMSE':mean_squared_error(y,pv)**0.5})
        for idx,val in enumerate(pv): preds.append({'model':name,'split':'grouped_cv','index':idx,'observed':float(y.iloc[idx]),'predicted':float(val),'composition':df.iloc[idx].composition,'T':float(df.iloc[idx]['T'])})
    pd.DataFrame(metrics).to_csv(outdir/'model_metrics.csv',index=False); pd.DataFrame(preds).to_csv(outdir/'predictions.csv',index=False)
    # fit best model on all data for screening
    best=models['ExtraTrees']; best.fit(X,y)
    imp=permutation_importance(best,X,y,n_repeats=5,random_state=42,n_jobs=1)
    pi=pd.DataFrame({'feature':cols,'importance_mean':imp.importances_mean,'importance_std':imp.importances_std}).sort_values('importance_mean',ascending=False)
    pi.to_csv(outdir/'permutation_importance.csv',index=False)
    return best,cols,metrics,df

def screen(best,cols,outdir):
    dopants=['Ag','Na','Cu','Sb','Te','Zn','Fe','Co','Ga']; ys=[0,0.01,0.03,0.05,0.10]; sevals=[0.0,0.03,0.06,0.12,0.20,0.50,0.80,1.0]; temps=[300,350,400,450,500,550,600]
    rows=[]; feat_rows=[]
    for d in dopants:
      for y in ys:
       for se in sevals:
        # dopant substitutes Sn; keep S+Se=1
        sn=1-y
        comp=f'Sn{sn:g}' + (f'{d}{y:g}' if y else '') + f'S{1-se:g}' + (f'Se{se:g}' if se else '')
        for T in temps:
         rows.append({'candidate':comp,'dopant':d,'dopant_fraction':y,'Se_fraction':se,'T_K':T,'extrapolation_flag':True})
         feat_rows.append(comp_features(comp,T))
    pred=best.predict(pd.DataFrame(feat_rows)[cols])
    for r,z in zip(rows,pred):
        r['predicted_ZT']=float(z); r['meets_ZT_ge_1']=bool(z>=1)
    out=pd.DataFrame(rows); out.to_csv(outdir/'candidate_screen.csv',index=False)
    # top candidates by worst-case predicted ZT across 300-600K
    agg=out.groupby('candidate').agg(min_ZT=('predicted_ZT','min'),mean_ZT=('predicted_ZT','mean'),max_ZT=('predicted_ZT','max'),all_T_ge_1=('meets_ZT_ge_1','all')).reset_index().sort_values(['all_T_ge_1','min_ZT','mean_ZT'],ascending=False)
    agg.to_csv(outdir/'candidate_ranked.csv',index=False); return out,agg

def plots(df, metrics, preds, imp, cand, outdir):
    plt.style.use('seaborn-v0_8-whitegrid'); p=Path(outdir)
    for m in sorted(set(x['model'] for x in metrics)):
      for split in ['heldout_groups','grouped_cv']:
       q=preds[(preds.model==m)&(preds.split==split)]
       if len(q)==0: continue
       fig,ax=plt.subplots(figsize=(6,5)); ax.scatter(q['observed'],q['predicted'],c=q['T'],cmap='viridis',s=22,alpha=.75); lo=min(q['observed'].min(),q['predicted'].min()); hi=max(q['observed'].max(),q['predicted'].max()); ax.plot([lo,hi],[lo,hi],'k--'); ax.set(xlabel='Observed ZT',ylabel='Predicted ZT',title=f'{m}: {split}'); fig.colorbar(ax.collections[0],label='Temperature (K)'); fig.tight_layout(); fig.savefig(p/f'{m}_{split}_parity.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5)); q=imp.head(20).sort_values('importance_mean'); ax.barh(q.feature,q.importance_mean,xerr=q.importance_std); ax.set_title('Permutation feature importance (ExtraTrees)'); fig.tight_layout(); fig.savefig(p/'feature_importance.png',dpi=180); plt.close(fig)
    top=cand[cand['candidate'].isin(pd.read_csv(Path(outdir).parent/'tables'/'candidate_ranked.csv').head(20).candidate)] if False else cand
    # screen heatmap for best candidates
    rank=pd.read_csv(Path(outdir).parent/'tables'/'candidate_ranked.csv').head(12); q=cand[cand.candidate.isin(rank.candidate)].pivot_table(index='candidate',columns='T_K',values='predicted_ZT'); fig,ax=plt.subplots(figsize=(10,6)); im=ax.imshow(q.values,aspect='auto',cmap='magma',vmin=0); ax.set_xticks(range(len(q.columns)),q.columns); ax.set_yticks(range(len(q.index)),q.index); ax.set_xlabel('Temperature (K)'); ax.set_title('Predicted ZT for screened Sn-S-Se doped candidates'); fig.colorbar(im,label='Predicted ZT'); fig.tight_layout(); fig.savefig(p/'candidate_ZT_heatmap.png',dpi=180); plt.close(fig)
    # empirical source curves
    for comp,g in df.groupby('composition'):
      if ('SnS' in comp or comp=='SnSe') and len(g)>=2:
       g=g.sort_values('T'); plt.plot(g['T'],g['ZT'],alpha=.55,label=comp)
    plt.xlabel('Temperature (K)'); plt.ylabel('ZT'); plt.title('Measured Sn-S-Se source curves'); plt.legend(fontsize=6,ncol=2); plt.tight_layout(); plt.savefig(p/'measured_snsse_curves.png',dpi=180); plt.close()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dataset-root',required=True); ap.add_argument('--out-dir',default='sn-s-se-advanced/outputs'); a=ap.parse_args(); out=Path(a.out_dir); (out/'tables').mkdir(parents=True,exist_ok=True); (out/'plots').mkdir(parents=True,exist_ok=True)
    df=load_training(a.dataset_root,out/'tables'); best,cols,metrics,df=evaluate_models(df,out/'tables'); cand,rank=screen(best,cols,out/'tables'); pred=pd.read_csv(out/'tables'/'predictions.csv'); imp=pd.read_csv(out/'tables'/'permutation_importance.csv'); plots(df,metrics,pred,imp,cand,out/'plots')
    summary={'rows':int(len(df)),'unique_compositions':int(df.group.nunique()),'features':cols,'metrics':metrics,'top_candidates':rank.head(20).to_dict('records'),'warning':'Candidate predictions are model extrapolations; no experimental/DFT stability validation was performed.'}; (out/'tables'/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
if __name__=='__main__': main()
