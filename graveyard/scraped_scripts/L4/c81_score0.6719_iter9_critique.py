import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

df0['Mouse ID'] = df0['Mouse ID'].astype(str)
df1['Mouse ID'] = df1['Mouse ID'].astype(str)

merged = pd.merge(df0, df1, on='Mouse ID', how='inner')

def sem(x):
    return x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0

# Aggregate Mouse ID by extracting digits and taking first value per group
def extract_mouse_id_int(s):
    # Extract digits from string, if none, return 0
    digits = ''.join(filter(str.isdigit, s))
    return int(digits) if digits else 0

# Apply aggregation
agg_df = merged.groupby(['Drug', 'Timepoint'], as_index=False).agg(
    **{
        'Mean of Metastatic Sites': ('Metastatic Sites', 'mean'),
        'SEM of Metastatic Sites': ('Metastatic Sites', sem),
        'Mouse ID': ('Mouse ID', lambda x: extract_mouse_id_int(x.iloc[0])),
        'Tumor Volume (mm3)': ('Tumor Volume (mm3)', 'mean')
    }
)

agg_df['Timepoint'] = agg_df['Timepoint'].astype(int)
agg_df['Mouse ID'] = agg_df['Mouse ID'].astype(int)
agg_df['Tumor Volume (mm3)'] = agg_df['Tumor Volume (mm3)'].round().astype(int)
agg_df['SEM of Metastatic Sites'] = agg_df['SEM of Metastatic Sites'].round().astype(int)

agg_df = agg_df[['Drug', 'Timepoint', 'Mean of Metastatic Sites', 'Mouse ID', 'Tumor Volume (mm3)', 'SEM of Metastatic Sites']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)