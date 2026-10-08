import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_1.csv", index_col=0)

agg_budget = df1.groupby("school_name")["budget"].sum()
agg_counts = df0.groupby("school_name")["Student ID"].count()
agg_math = df0.groupby("school_name")["math_score"].mean()
agg_reading = df0.groupby("school_name")["reading_score"].mean()

result = pd.DataFrame({
    "school_name": agg_budget.index,
    "budget": agg_budget.values,
    "Student ID": agg_counts.reindex(agg_budget.index).values,
    "math_score": agg_math.reindex(agg_budget.index).values,
    "reading_score": agg_reading.reindex(agg_budget.index).values
})

result["Student ID"] = result["Student ID"].astype("Int64")
result["budget"] = result["budget"].astype("Int64")
result["math_score"] = result["math_score"].astype(float)
result["reading_score"] = result["reading_score"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_24/target_multisource_mcts.csv", index=False)