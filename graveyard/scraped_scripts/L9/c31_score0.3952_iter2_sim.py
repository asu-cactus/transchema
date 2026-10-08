import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)

sum_home_passed = (
    df0['HOME_PASSED'].sum()
    + df1['HOME_PASSED'].sum()
    + df3['HOME_PASSED'].sum()
    + df5['HOME_PASSED'].sum()
)

result = pd.DataFrame({'HOME_PASSED': [int(sum_home_passed)]})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)