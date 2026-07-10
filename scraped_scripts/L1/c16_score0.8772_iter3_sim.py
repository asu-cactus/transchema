import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="CUSTOMERNAME", suffixes=('_left', '_right'))

grouped = joined.groupby("CUSTOMERNAME", as_index=False).agg({"ORDERNUMBER_left": "count"})

grouped = grouped.rename(columns={"ORDERNUMBER_left": "ORDERNUMBER"})

grouped["ORDERNUMBER"] = grouped["ORDERNUMBER"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)