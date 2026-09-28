import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="PRODUCTCODE", suffixes=('_left', '_right'))

grouped = joined.groupby("PRODUCTLINE_left", dropna=False, as_index=False).agg({"SALES_left": "sum"})

result = grouped.rename(columns={"PRODUCTLINE_left": "PRODUCTLINE", "SALES_left": "SALES"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)