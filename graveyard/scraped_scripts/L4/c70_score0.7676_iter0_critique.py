import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_70/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_70/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_70/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_70/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_70/training_4.csv"
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    # Convert GEO.id to string
    df['GEO.id'] = df['GEO.id'].astype(str)
    # Convert GEO.id2 to int first (to remove .0), then to string
    # Some GEO.id2 values are floats with .0, so convert safely
    df['GEO.id2'] = pd.to_numeric(df['GEO.id2'], errors='coerce').fillna(0).astype(int).astype(str)
    # GEO.display-label to string
    df['GEO.display-label'] = df['GEO.display-label'].astype(str)
    # HD01_VD01 and HD02_VD01 to string (some are numeric)
    df['HD01_VD01'] = df['HD01_VD01'].astype(str)
    df['HD02_VD01'] = df['HD02_VD01'].astype(str)
    # Year to int
    df['Year'] = df['Year'].astype(int)
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_70/target_multisource_mcts.csv", index=False)