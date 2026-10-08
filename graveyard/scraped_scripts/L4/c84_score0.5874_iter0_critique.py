import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv"
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    # Drop the 'Unnamed: 1' column as it is not in target schema
    if 'Unnamed: 1' in df.columns:
        df = df.drop(columns=['Unnamed: 1'])
    # Filter out rows where 'age_grp' is not a valid age group (e.g., remove rows where age_grp is 'Year' or 'Total for selection')
    df = df[~df['age_grp'].isin(['Year', 'Total for selection'])]
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

# Convert columns to correct types
df['age_grp'] = df['age_grp'].astype(str)
df['Count'] = pd.to_numeric(df['Count'], errors='coerce')
df['Notes'] = df['Notes'].astype(str).replace({'nan': pd.NA})
df['Rate'] = pd.to_numeric(df['Rate'], errors='coerce')
df['Statistics'] = df['Statistics'].astype(str).replace({'nan': pd.NA})

# Group by 'age_grp' and 'Statistics' and aggregate
agg_df = df.groupby(['age_grp', 'Statistics'], dropna=False).agg({
    'Count': 'sum',
    'Rate': 'mean',
    'Notes': lambda x: x.dropna().iloc[0] if not x.dropna().empty else pd.NA
}).reset_index()

# Reorder columns to match target schema
agg_df = agg_df[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)