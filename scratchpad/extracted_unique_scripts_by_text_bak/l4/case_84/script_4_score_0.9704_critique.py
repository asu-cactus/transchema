import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    # Keep only rows where 'age_grp' is not 'Year' or 'Total for selection' or other non-age groups
    # We assume valid age_grp values do not contain 'Year' or 'Total for selection'
    df = df[~df['age_grp'].isin(['Year', 'Total for selection'])]
    # Select only required columns
    df = df[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Convert columns to correct types
df_all['age_grp'] = df_all['age_grp'].astype(str)
df_all['Count'] = pd.to_numeric(df_all['Count'], errors='coerce')
df_all['Notes'] = df_all['Notes'].astype(str).replace({'nan': pd.NA})
df_all['Rate'] = pd.to_numeric(df_all['Rate'], errors='coerce')
df_all['Statistics'] = df_all['Statistics'].astype(str).replace({'nan': pd.NA})

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)