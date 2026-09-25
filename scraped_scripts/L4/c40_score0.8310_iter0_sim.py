import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df_grouped = df.groupby('y').agg({
    'x': 'mean',
    'label': lambda s: pd.to_numeric(s.astype('category').cat.codes, errors='coerce').mode().iloc[0] if not s.empty else pd.NA
}).reset_index()

df_grouped['x'] = df_grouped['x'].astype(float)
df_grouped['y'] = df_grouped['y'].astype(int)
df_grouped['label'] = df_grouped['label'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)