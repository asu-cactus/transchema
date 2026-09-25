import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID")

result = merged[["Drug", "Timepoint", "Mouse ID"]]

result["Timepoint"] = result["Timepoint"].astype(int)
result["Mouse ID"] = result["Mouse ID"].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if any(c.isdigit() for c in str(x)) else pd.NA)
result = result.dropna(subset=["Mouse ID"])
result["Mouse ID"] = result["Mouse ID"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)