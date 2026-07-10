import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

agg0 = df0.groupby("State").agg(
    Participation_x=("Participation", lambda x: str(len(x)) + "%"),
    English=("English", "mean"),
    Math_x=("Math", "mean"),
    Reading=("Reading", "mean"),
    Science=("Science", "mean"),
    Composite=("Composite", "mean"),
).reset_index()

agg1 = df1.groupby("State").agg(
    Participation_y=("Participation", lambda x: str(len(x)) + "%"),
    Evidence_Based_Reading_and_Writing=("Evidence-Based Reading and Writing", "mean"),
    Math_y=("Math", "mean"),
    Total=("Total", "mean"),
).reset_index()

merged = pd.merge(agg0, agg1, how="inner", left_on="State", right_on="State")

merged["Participation_x"] = merged["Participation_x"].str.replace("%", "") + "%"
merged["Participation_y"] = merged["Participation_y"].str.replace("%", "") + "%"

merged["Evidence-Based Reading and Writing"] = merged["Evidence_Based_Reading_and_Writing"].round().astype("Int64")
merged["Math_y"] = merged["Math_y"].round().astype("Int64")
merged["Total"] = merged["Total"].round().astype("Int64")

merged = merged.rename(columns={
    "Evidence_Based_Reading_and_Writing": "Evidence-Based Reading and Writing"
})

result = merged[
    [
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
        "Total",
    ]
]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)