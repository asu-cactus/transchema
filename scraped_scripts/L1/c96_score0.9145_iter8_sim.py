import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)

agg = df0.groupby("Publisher", dropna=False).agg({"name": "count"}).reset_index()
agg.columns = ["Publisher", "Publisher_count"]

agg["Publisher"] = agg["Publisher"].astype(str).str.strip()
agg = agg[agg["Publisher"] != ""]  # remove empty publisher if any

agg["Publisher_count"] = agg["Publisher_count"].astype(int)

agg = agg.rename(columns={"Publisher_count": "Publisher"})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)