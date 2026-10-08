import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_39/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="Mouse ID")

result = df.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).size()

result = result.rename(columns={"Drug": "Drug", "Timepoint": "Timepoint", "Mouse ID": "Mouse ID"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_39/target_multisource_mcts.csv", index=False)