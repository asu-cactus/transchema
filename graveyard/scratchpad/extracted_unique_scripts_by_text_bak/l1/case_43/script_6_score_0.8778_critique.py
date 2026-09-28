import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Group by fac_type
agg_df = df.groupby("fac_type").agg(
    facid=pd.NamedAgg(column="facid", aggfunc="count"),
    capacity=pd.NamedAgg(column="capacity", aggfunc="sum"),
    fac_name=pd.NamedAgg(column="fac_name", aggfunc=lambda x: x.nunique()),
    fac_address=pd.NamedAgg(column="fac_address", aggfunc=lambda x: x.nunique()),
    city_state_zip=pd.NamedAgg(column="city_state_zip", aggfunc=lambda x: x.nunique()),
    owner=pd.NamedAgg(column="owner", aggfunc=lambda x: x.nunique()),
    operator=pd.NamedAgg(column="operator", aggfunc=lambda x: x.nunique()),
).reset_index()

# Ensure correct dtypes as per target schema
agg_df["facid"] = agg_df["facid"].astype(int)
agg_df["capacity"] = agg_df["capacity"].astype(int)
agg_df["fac_name"] = agg_df["fac_name"].astype(int)
agg_df["fac_address"] = agg_df["fac_address"].astype(int)
agg_df["city_state_zip"] = agg_df["city_state_zip"].astype(int)
agg_df["owner"] = agg_df["owner"].astype(int)
agg_df["operator"] = agg_df["operator"].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)