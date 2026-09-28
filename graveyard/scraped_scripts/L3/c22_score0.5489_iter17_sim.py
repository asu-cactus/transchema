import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)

agg = df0.groupby("Department").agg({
    "Max Units": "min",
    "Min Units": "max",
    "Reg Count": "mean"
}).reset_index()

agg.rename(columns={
    "Department": "Department",
    "Max Units": "20153",
    "Min Units": "20161",
    "Reg Count": "20162"
}, inplace=True)

agg["20153"] = agg["20153"].astype(float)
agg["20161"] = agg["20161"].astype(float)
agg["20162"] = agg["20162"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)