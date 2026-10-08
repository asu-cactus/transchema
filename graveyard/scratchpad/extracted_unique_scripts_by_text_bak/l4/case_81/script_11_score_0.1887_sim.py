import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

df_merged = pd.merge(df0, df1, on="Mouse ID")

agg_mean = df_merged.groupby(['Mouse ID', 'Drug', 'Timepoint', 'Tumor Volume (mm3)'])['Metastatic Sites'].mean().rename('Mean of Metastatic Sites')
agg_sem = df_merged.groupby(['Mouse ID', 'Drug', 'Timepoint', 'Tumor Volume (mm3)'])['Metastatic Sites'].sem().fillna(0).rename('SEM of Metastatic Sites')

df_agg = pd.concat([agg_mean, agg_sem], axis=1).reset_index()

df_agg['Drug'] = df_agg['Drug'].astype(str)
df_agg['Timepoint'] = df_agg['Timepoint'].astype(int)
df_agg['Mean of Metastatic Sites'] = df_agg['Mean of Metastatic Sites'].astype(float)
df_agg['Tumor Volume (mm3)'] = df_agg['Tumor Volume (mm3)'].round().astype(int)
df_agg['SEM of Metastatic Sites'] = df_agg['SEM of Metastatic Sites'].round().astype(int)

def mouse_id_to_int(mid):
    try:
        return int(mid)
    except:
        return pd.NA

df_agg['Mouse ID'] = df_agg['Mouse ID'].apply(mouse_id_to_int)

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)