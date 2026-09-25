import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_13/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_13/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_13/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

result = df[['sex', 'smoker', 'tip_pct']].copy()
result['sex'] = result['sex'].astype(str)
result['smoker'] = result['smoker'].astype(str)
result['tip_pct'] = result['tip_pct'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)