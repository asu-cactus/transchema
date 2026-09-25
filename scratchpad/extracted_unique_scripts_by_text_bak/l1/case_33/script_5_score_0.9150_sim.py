import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

agg_df0 = df0.groupby("State", as_index=False).agg({
    "English": "mean",
    "Math": "mean",
    "Reading": "mean",
    "Science": "mean",
    "Composite": "mean",
    "Participation": "first"
}).rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

joined = pd.merge(agg_df0, df1, on="State", how="inner")

joined = joined.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

result = joined[[
    "State",
    "Participation_x",
    "English",
    "Math_x",
    "Reading",
    "Science",
    "Composite",
    "Participation_y",
    "Evidence-Based Reading and Writing",
    "Math_y",
    "Total"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv", index=False)