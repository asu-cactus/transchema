import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

pivot_result = df0.rename(columns={"Participation": "Participation_y"})
pivot_result = pivot_result.rename(columns={"Math": "Math_x", "Participation_y": "Participation_x"})
pivot_result = pivot_result.rename(columns={"Participation_x": "Participation_x", "Participation_y": "Participation_y"})

pivot_result = pivot_result.rename(columns={"Participation_y": "Participation_x"})
pivot_result = pivot_result.rename(columns={"Participation": "Participation_x"})

pivot_result = df0.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})

# The partial plan says PIVOT and GROUP_BY on Participation_y, but here Participation_y is not in df0.
# Actually, Participation_y is from df1, so we keep Participation in df0 as Participation_x.
# So rename Participation in df0 to Participation_x.
pivot_result = df0.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})

# Join on State and Participation_y = Participation in df1
# So rename Participation in df1 to Participation_y to match target schema
df1_renamed = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

merged = pd.merge(pivot_result, df1_renamed, how="inner", on=["State"])

# Reorder and select columns to match target schema
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

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)