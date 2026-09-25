import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

agg0 = df0.groupby("State", as_index=False).agg({
    "Participation": "sum",
    "English": "sum",
    "Math": "sum",
    "Reading": "sum",
    "Science": "sum",
    "Composite": "sum"
})

agg1 = df1.groupby("State", as_index=False).agg({
    "Participation": "sum",
    "Evidence-Based Reading and Writing": "sum",
    "Math": "sum",
    "Total": "sum"
})

merged = pd.merge(agg0, agg1, on="State", suffixes=("_x", "_y"))

merged["Participation_x"] = merged["Participation_x"].astype(str)
merged["Participation_y"] = merged["Participation_y"].astype(str)

merged = merged.rename(columns={
    "English": "English",
    "Math_x": "Math_x",
    "Reading": "Reading",
    "Science": "Science",
    "Composite": "Composite",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "Math_y": "Math_y",
    "Total": "Total"
})

final_cols = [
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
]

result = merged[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)