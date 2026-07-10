import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)

pivot_df = df.pivot_table(index='condition', columns='click', aggfunc='size', fill_value=0).reset_index()

if 0 not in pivot_df.columns:
    pivot_df[0] = 0

result = pivot_df[['condition', 0]].astype({'condition': int, 0: int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)