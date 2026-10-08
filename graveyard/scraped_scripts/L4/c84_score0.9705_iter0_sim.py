import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['age_grp'] = df['age_grp'].astype(str)
df['Count'] = pd.to_numeric(df['Count'], errors='coerce')
df['Notes'] = df['Notes'].astype(str).replace('nan', pd.NA)
df['Rate'] = pd.to_numeric(df['Rate'], errors='coerce')
df['Statistics'] = df['Statistics'].astype(str).replace('nan', pd.NA)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)