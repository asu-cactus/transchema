import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_1.csv", index_col=0)

agg = df1.groupby('Mouse ID').agg(
    Timepoint_min=('Timepoint', 'min'),
    Timepoint_max=('Timepoint', 'max'),
    Tumor_Volume_avg=('Tumor Volume (mm3)', 'mean'),
    Metastatic_Sites_sum=('Metastatic Sites', 'sum')
).reset_index()

merged = pd.merge(agg, df0, on='Mouse ID', how='inner')

# The target schema is ['Drug': string, 'Timepoint': integer, 'Mouse ID': integer]
# The target examples show a single Timepoint column, but the aggregation produced min and max.
# We choose the min Timepoint as the representative Timepoint (consistent with example).
# Also, Mouse ID in source is string, but target expects integer. We convert Mouse ID to integer if possible.
# However, source Mouse ID looks like strings (e.g., 'f234'), so we keep as string to avoid data loss.
# Instead, we cast Timepoint to int.

merged['Timepoint'] = merged['Timepoint_min'].astype(int)
result = merged[['Drug', 'Timepoint', 'Mouse ID']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_64/target_multisource_mcts.csv", index=False)