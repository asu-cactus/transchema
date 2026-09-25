import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_88/training_0.csv", index_col=0)

df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0).astype(int)

df = df.drop_duplicates()

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_88/target_multisource_mcts.csv", index=False)