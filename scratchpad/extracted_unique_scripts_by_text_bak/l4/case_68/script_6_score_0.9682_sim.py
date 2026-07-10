import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg0 = df0.groupby("school_name").agg(
    a_min_type = ("type", "min"),
    b_sum_size = ("size", "sum"),
    c_sum_budget = ("budget", "sum")
).reset_index()

agg1 = df1.groupby("school_name").agg(
    d_mean_reading_score = ("reading_score", "mean"),
    e_mean_math_score = ("math_score", "mean")
).reset_index()

merged = pd.merge(agg0, agg1, on="school_name", how="inner")

merged["a"] = merged["a_min_type"].astype(str)
merged["b"] = merged["b_sum_size"].astype(int)
merged["c"] = merged["c_sum_budget"].astype(int)
merged["d"] = merged["d_mean_reading_score"].astype(float)
merged["e"] = merged["e_mean_math_score"].astype(float)

result = merged[["school_name", "a", "b", "c", "d", "e"]]

result.to_csv(target_path, index=False)