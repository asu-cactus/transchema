import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg_df = df0.groupby("fac_type").agg(
    facid=("facid", lambda x: pd.to_numeric(x, errors='coerce').min()),
    capacity=("capacity", "max"),
    fac_name=("fac_name", lambda x: pd.to_numeric(x, errors='coerce').min()),
    fac_address=("fac_address", lambda x: pd.to_numeric(x, errors='coerce').min()),
    city_state_zip=("city_state_zip", lambda x: pd.to_numeric(x, errors='coerce').min()),
    owner=("owner", lambda x: pd.to_numeric(x, errors='coerce').min()),
    operator=("operator", lambda x: pd.to_numeric(x, errors='coerce').min()),
).reset_index()

agg_df["facid"] = agg_df["facid"].astype("Int64")
agg_df["capacity"] = agg_df["capacity"].astype("Int64")
agg_df["fac_name"] = agg_df["fac_name"].astype("Int64")
agg_df["fac_address"] = agg_df["fac_address"].astype("Int64")
agg_df["city_state_zip"] = agg_df["city_state_zip"].astype("Int64")
agg_df["owner"] = agg_df["owner"].astype("Int64")
agg_df["operator"] = agg_df["operator"].astype("Int64")

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)