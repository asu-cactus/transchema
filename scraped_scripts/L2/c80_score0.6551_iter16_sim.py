import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_80/training_0.csv", index_col=0)

grouped = df0.groupby(df0.columns[0]).agg({
    df0.columns[2]: ['sum', 'max'],
    df0.columns[1]: 'min'
})

grouped.columns = ['1', '2', '3']
grouped = grouped.reset_index()
grouped.rename(columns={grouped.columns[0]: '0'}, inplace=True)

grouped = grouped.astype({'0': float, '1': float, '2': float, '3': float})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_80/target_multisource_mcts.csv", index=False)