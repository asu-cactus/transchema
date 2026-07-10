import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_58/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_58/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_58/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on 'State' with inner join
merged = pd.merge(df0, df1, how="inner", on="State", suffixes=('_x', '_y'))

# Rename columns to match target schema exactly
result = pd.DataFrame()
result["State"] = merged["State"]
result["Participation_x"] = merged["Participation_x"]
result["Evidence-Based Reading and Writing"] = merged["Evidence-Based Reading and Writing"].astype(int)
result["Math_x"] = merged["Math_x"].astype(int)
result["Total"] = merged["Total"].astype(int)
result["Participation_y"] = merged["Participation_y"]
result["English"] = merged["English"].astype(float)
result["Math_y"] = merged["Math_y"].astype(float)
result["Reading"] = merged["Reading"].astype(float)
result["Science"] = merged["Science"].astype(float)
result["Composite"] = merged["Composite"].astype(float)

result.to_csv(target_path, index=False)