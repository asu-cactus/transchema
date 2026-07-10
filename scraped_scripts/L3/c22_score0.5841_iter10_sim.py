import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)

agg = df0.groupby("Department").agg(
    min_reg_count=pd.NamedAgg(column="Reg Count", aggfunc="min"),
    max_reg_count=pd.NamedAgg(column="Reg Count", aggfunc="max"),
    avg_seats=pd.NamedAgg(column="Seats", aggfunc="mean")
).reset_index()

agg = agg.rename(columns={"Department": "Department"})

agg = agg.rename(columns={
    "min_reg_count": "20153",
    "max_reg_count": "20161",
    "avg_seats": "20162"
})

agg["20153"] = agg["20153"].astype(float)
agg["20161"] = agg["20161"].astype(float)
agg["20162"] = agg["20162"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)