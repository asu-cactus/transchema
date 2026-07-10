import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_2.csv", index_col=0)

join_result = pd.merge(s2, s1, on="state", how="inner")

join_result["year"] = join_result["year"].astype("Int64")
join_result["draw_sales"] = join_result["draw_sales"].astype("Int64")
join_result["full_state"] = join_result["full_state"].astype("Int64", errors="ignore")
join_result["pop"] = join_result["pop"].astype("Int64", errors="ignore")

s0["year"] = pd.to_datetime(s0["date"]).dt.year.astype("Int64")
s0["draw_sales"] = s0["draw_sales"].astype("Int64")
s0["full_state"] = pd.NA
s0["pop"] = pd.NA

s0 = s0[["state", "year", "draw_sales", "full_state", "pop"]]
join_result = join_result[["state", "year", "draw_sales", "full_state", "pop"]]

result = pd.concat([s0, join_result], ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_6/target_multisource_mcts.csv", index=False)