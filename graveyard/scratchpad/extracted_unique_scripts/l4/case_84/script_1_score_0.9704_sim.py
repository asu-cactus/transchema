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
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Ensure columns are exactly as target schema and types
df_all = df_all[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]

df_all['age_grp'] = df_all['age_grp'].astype(str)
df_all['Count'] = pd.to_numeric(df_all['Count'], errors='coerce')
df_all['Notes'] = df_all['Notes'].astype(str).replace({'nan': pd.NA})
df_all['Rate'] = pd.to_numeric(df_all['Rate'], errors='coerce')
df_all['Statistics'] = df_all['Statistics'].astype(str).replace({'nan': pd.NA})

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)