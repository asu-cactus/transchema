import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_51/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_51/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_51/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

union_result = df0.copy()

merged = union_result.merge(df1, on="school_name", how="left")

final = merged[[
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

final["Student ID"] = final["Student ID"].astype("Int64")
final["reading_score"] = final["reading_score"].astype("Int64")
final["math_score"] = final["math_score"].astype("Int64")
final["School ID"] = final["School ID"].astype("Int64")
final["size"] = final["size"].astype("Int64")
final["budget"] = final["budget"].astype("Int64")

final.to_csv(target_path, index=False)