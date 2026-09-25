import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

df0 = df0.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})
df1 = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

merged = pd.merge(df0, df1, on="State", how="inner")

grouped = merged.groupby(["Participation_y", "Participation_x"], as_index=False).agg({
    "State": "first",
    "English": "mean",
    "Math_x": "mean",
    "Reading": "mean",
    "Science": "mean",
    "Composite": "mean",
    "Evidence-Based Reading and Writing": "sum",
    "Math_y": "sum",
    "Total": "sum"
})

cols_order = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
              'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = grouped[cols_order]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv", index=False)