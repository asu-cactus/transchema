import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

pivot_result = df0.pivot(columns='right_index', values='0').reset_index(drop=True)
pivot_result.columns = [f"0_x" if col == 0 else col for col in pivot_result.columns]

result = pivot_result.join(df1)
result = result.rename(columns={0: "0_y"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)