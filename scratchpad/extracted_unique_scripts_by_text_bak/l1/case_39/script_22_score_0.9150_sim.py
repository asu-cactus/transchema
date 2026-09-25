import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

agg = df0.groupby("State").agg({
    "English": "min",
    "Math": "min",
    "Reading": "min",
    "Science": "min",
    "Composite": "min"
}).reset_index()

agg = agg.rename(columns={
    "Math": "Math_x"
})

df1_renamed = df1.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

df0_participation = df0.groupby("State")["Participation"].min().reset_index().rename(columns={"Participation": "Participation_x"})

merged = pd.merge(agg, df0_participation, on="State", how="left")
merged = pd.merge(merged, df1_renamed, on="State", how="left")

result = merged[[
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

result["English"] = result["English"].astype(float)
result["Math_x"] = result["Math_x"].astype(float)
result["Reading"] = result["Reading"].astype(float)
result["Science"] = result["Science"].astype(float)
result["Composite"] = result["Composite"].astype(float)
result["Evidence-Based Reading and Writing"] = pd.to_numeric(result["Evidence-Based Reading and Writing"], errors='coerce').astype('Int64')
result["Math_y"] = pd.to_numeric(result["Math_y"], errors='coerce').astype('Int64')
result["Total"] = pd.to_numeric(result["Total"], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)