import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, left_on="scientific_name", right_on="scientific_name", suffixes=('', '_y'))

grouped = joined.groupby("conservation_status", dropna=False).agg(scientific_name=('scientific_name', 'count')).reset_index()

grouped['scientific_name'] = grouped['scientific_name'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)