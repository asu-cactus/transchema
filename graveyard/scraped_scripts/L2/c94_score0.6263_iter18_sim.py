import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_94/training_0.csv", index_col=0)

grouped = df0.groupby(df0.columns[0]).agg({
    df0.columns[2]: 'count',
    df0.columns[3]: 'count',
    df0.columns[1]: 'mean'
}).reset_index()

grouped.columns = ['0', '1', '2', '3']
grouped = grouped.astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_94/target_multisource_mcts.csv", index=False)