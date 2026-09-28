import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_76/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_76/training_1.csv", index_col=0)

pivot = source1.pivot_table(index='school_name', columns='grade', values='reading_score', aggfunc='mean').reset_index()

pivot['mean_reading_score'] = pivot.loc[:, pivot.columns != 'school_name'].mean(axis=1)

merged = pd.merge(pivot[['school_name', 'mean_reading_score']], source0[['school_name']], on='school_name', how='inner')

result = merged.rename(columns={'mean_reading_score': 'reading_score'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_76/target_multisource_mcts.csv", index=False)