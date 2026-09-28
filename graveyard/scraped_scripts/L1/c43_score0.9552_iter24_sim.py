import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg = df0.groupby("fac_type").agg(capacity_min=("capacity", "min"), capacity_max=("capacity", "max")).reset_index()

agg["capacity"] = agg["capacity_max"]
agg["facid"] = agg["capacity_max"]
agg["fac_name"] = agg["capacity_max"]
agg["fac_address"] = agg["capacity_max"]
agg["city_state_zip"] = agg["capacity_max"]
agg["owner"] = agg["capacity_max"]
agg["operator"] = agg["capacity_max"]

result = agg[["fac_type", "facid", "capacity", "fac_name", "fac_address", "city_state_zip", "owner", "operator"]]

result["facid"] = result["facid"].astype("Int64")
result["capacity"] = result["capacity"].astype("Int64")
result["fac_name"] = result["fac_name"].astype("Int64")
result["fac_address"] = result["fac_address"].astype("Int64")
result["city_state_zip"] = result["city_state_zip"].astype("Int64")
result["owner"] = result["owner"].astype("Int64")
result["operator"] = result["operator"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)