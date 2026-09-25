import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_1.csv", index_col=0)

agg0 = df0.groupby("State", as_index=False).agg({
    "Participation": lambda x: x.str.rstrip('%').astype(float).sum(),
    "English": "sum",
    "Math": "sum",
    "Reading": "sum",
    "Science": "sum",
    "Composite": "sum"
})
agg0["Participation"] = agg0["Participation"].astype(str) + "%"

agg1 = df1.groupby("State", as_index=False).agg({
    "Participation": lambda x: x.str.rstrip('%').astype(float).sum(),
    "Evidence-Based Reading and Writing": "sum",
    "Math": "sum",
    "Total": "sum"
})
agg1["Participation"] = agg1["Participation"].astype(str) + "%"

merged = pd.merge(agg0, agg1, on="State", suffixes=("_x", "_y"))

merged = merged.rename(columns={
    "Participation_x": "Participation_x",
    "English": "English",
    "Math_x": "Math_x",
    "Reading": "Reading",
    "Science": "Science",
    "Composite": "Composite",
    "Participation_y": "Participation_y",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "Math_y": "Math_y",
    "Total": "Total"
})

merged = merged[[
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

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_63/target_multisource_mcts.csv", index=False)