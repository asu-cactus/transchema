import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/test_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/test_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/test_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/test_3.csv", index_col=0)

combined = pd.concat([df0, df1, df2, df3], axis=0)
grouped = combined.groupby("company", as_index=False).size()
result = grouped.rename(columns={"size": "count"})

result["title"] = result["count"]
result["location"] = result["count"]
result["summary"] = result["count"]
result["salary"] = result["count"]
result["href"] = result["count"]
result["rate"] = result["count"]
result["reviews"] = result["count"]
result["org_salary_period"] = result["count"]

result = result[["company", "title", "location", "summary", "salary", "href", "rate", "reviews", "org_salary_period"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts_recovery_test_val.csv", index=False)