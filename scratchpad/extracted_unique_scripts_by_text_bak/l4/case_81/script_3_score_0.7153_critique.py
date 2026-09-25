import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_81/training_1.csv", index_col=0)

# Join on Mouse ID (string)
df_merged = pd.merge(df0, df1, on="Mouse ID", how='inner')

# Group by Drug and Timepoint (leftmost non-float columns in target)
grouped = df_merged.groupby(['Drug', 'Timepoint'])

# Aggregations:
# Mean of Metastatic Sites (float)
mean_met_sites = grouped['Metastatic Sites'].mean().rename('Mean of Metastatic Sites')

# Count distinct Mouse ID (integer)
count_mouse_id = grouped['Mouse ID'].nunique().rename('Mouse ID')

# Mean Tumor Volume rounded to int
mean_tumor_vol = grouped['Tumor Volume (mm3)'].mean().round().astype(int).rename('Tumor Volume (mm3)')

# SEM of Metastatic Sites rounded to int
sem_met_sites = grouped['Metastatic Sites'].sem().fillna(0).round().astype(int).rename('SEM of Metastatic Sites')

# Combine all
df_result = pd.concat([mean_met_sites, count_mouse_id, mean_tumor_vol, sem_met_sites], axis=1).reset_index()

# Ensure types match target schema
df_result['Drug'] = df_result['Drug'].astype(str)
df_result['Timepoint'] = df_result['Timepoint'].astype(int)
df_result['Mean of Metastatic Sites'] = df_result['Mean of Metastatic Sites'].astype(float)
df_result['Mouse ID'] = df_result['Mouse ID'].astype(int)
df_result['Tumor Volume (mm3)'] = df_result['Tumor Volume (mm3)'].astype(int)
df_result['SEM of Metastatic Sites'] = df_result['SEM of Metastatic Sites'].astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_81/target_multisource_mcts.csv", index=False)