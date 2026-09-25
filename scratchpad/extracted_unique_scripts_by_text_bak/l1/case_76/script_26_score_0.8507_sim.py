import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_76/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_76/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_76/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df0, df1, on="school_name", how="inner")

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

merged["Student ID"] = merged["Student ID"].astype(int)
merged["reading_score"] = merged["reading_score"].astype(int)
merged["math_score"] = merged["math_score"].astype(int)
merged["School ID"] = merged["School ID"].astype(int)
merged["size"] = merged["size"].astype(int)
merged["budget"] = merged["budget"].astype(int)

merged.to_csv(target_path, index=False)