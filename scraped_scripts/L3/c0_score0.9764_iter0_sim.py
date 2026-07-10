import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_0/training_0.csv", index_col=0)

agg = df0.groupby("SN").agg(
    **{
        "Total Purchase Value": ("Price", "sum"),
        "Purchase Count": ("Purchase ID", "count"),
    }
).reset_index()

agg["SN"] = agg["SN"].astype(str)
agg["Total Purchase Value"] = agg["Total Purchase Value"].astype(float)
agg["Purchase Count"] = agg["Purchase Count"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_0/target_multisource_mcts.csv", index=False)