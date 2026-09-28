import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_31/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_31/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_31/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped_source0 = df0.groupby("State", as_index=False).agg({
    "Participation": "first",
    "Evidence-Based Reading and Writing": "sum",
    "Math": "sum",
    "Total": "sum"
}).rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

joined = pd.merge(grouped_source0, df1, on="State", how="inner")

joined = joined.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

joined = joined[[
    "State",
    "Participation_x",
    "Evidence-Based Reading and Writing",
    "Math_x",
    "Total",
    "Participation_y",
    "English",
    "Math_y",
    "Reading",
    "Science",
    "Composite"
]]

joined["Participation_x"] = joined["Participation_x"].astype(str)
joined["Participation_y"] = joined["Participation_y"].astype(str)
joined["Evidence-Based Reading and Writing"] = joined["Evidence-Based Reading and Writing"].astype(int)
joined["Math_x"] = joined["Math_x"].astype(int)
joined["Total"] = joined["Total"].astype(int)
joined["English"] = joined["English"].astype(float)
joined["Math_y"] = joined["Math_y"].astype(float)
joined["Reading"] = joined["Reading"].astype(float)
joined["Science"] = joined["Science"].astype(float)
joined["Composite"] = joined["Composite"].astype(float)

joined.to_csv(target_path, index=False)