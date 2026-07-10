import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

result = df0.groupby("condition", as_index=False).agg(click=pd.NamedAgg(column="click", aggfunc=lambda x: x.nunique()))
result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)