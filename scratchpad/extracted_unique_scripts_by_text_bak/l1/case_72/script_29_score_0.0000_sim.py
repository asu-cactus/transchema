import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_72/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

pivoted = df.groupby(['condition', 'click']).size().unstack(fill_value=0)
pivoted = pivoted.rename(columns={0: '0'})
pivoted = pivoted.reset_index()

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)