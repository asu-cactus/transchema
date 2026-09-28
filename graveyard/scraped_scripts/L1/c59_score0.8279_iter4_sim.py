import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, left_on="ORDERNUMBER", right_on="ORDERNUMBER", suffixes=('_left', '_right'))

result = joined.groupby("PRODUCTLINE_left", dropna=False, as_index=False)["SALES_left"].sum()

result.columns = ["PRODUCTLINE", "SALES"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)