import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_28/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_28/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_28/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df1, df0, how="inner", on="school_name")

merged = merged[[
    "Student ID",
    "student_name",
    "gender",
    "grade",
    "school_name",
    "reading_score",
    "math_score",
    "School ID",
    "type",
    "size",
    "budget"
]]

merged.to_csv(target_path, index=False)