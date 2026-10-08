import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_95/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, left_on="school", right_on="name", how="inner")

result = pd.DataFrame()
result["School Name"] = merged["school"]
result["Student Grade"] = merged["grade"]
result["School ID"] = merged["School ID"].astype("Int64")
result["School Size"] = merged["size"].astype("Int64")
result["School Budget"] = merged["budget"].astype("Int64")
result["Student ID"] = merged["Student ID"].astype(float)
result["Student Reading Score"] = merged["reading_score"].astype(float)
result["Average Student Math Score"] = merged["math_score"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_95/target_multisource_mcts.csv", index=False)