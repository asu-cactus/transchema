import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_1.csv", index_col=0)

# Join on Mouse ID
df = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Group by Mouse ID and Timepoint, aggregate Drug by first
df_grouped = df.groupby(['Mouse ID', 'Timepoint'], as_index=False).agg({'Drug': 'first'})

# Reorder columns to match target schema: ['Drug', 'Timepoint', 'Mouse ID']
df_grouped = df_grouped[['Drug', 'Timepoint', 'Mouse ID']]

# Convert Mouse ID to integer if possible (assuming Mouse ID strings represent integers)
# If Mouse ID cannot be converted directly, map unique Mouse IDs to integers
try:
    df_grouped['Mouse ID'] = pd.to_numeric(df_grouped['Mouse ID'], errors='raise').astype(int)
except:
    # Map unique Mouse IDs to integers
    mouse_id_map = {mid: idx for idx, mid in enumerate(sorted(df_grouped['Mouse ID'].unique()), start=1)}
    df_grouped['Mouse ID'] = df_grouped['Mouse ID'].map(mouse_id_map).astype(int)

# Ensure Timepoint is integer
df_grouped['Timepoint'] = pd.to_numeric(df_grouped['Timepoint'], errors='coerce').astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_93/target_multisource_mcts.csv", index=False)