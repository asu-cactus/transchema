import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg = df0.groupby("fac_type").agg(
    facid=pd.NamedAgg(column="facid", aggfunc=lambda x: x.nunique()),
    capacity=pd.NamedAgg(column="capacity", aggfunc=lambda x: x.nunique()),
    fac_name=pd.NamedAgg(column="fac_name", aggfunc=lambda x: x.nunique()),
    fac_address=pd.NamedAgg(column="fac_address", aggfunc=lambda x: x.nunique()),
    city_state_zip=pd.NamedAgg(column="city_state_zip", aggfunc=lambda x: x.nunique()),
    owner=pd.NamedAgg(column="owner", aggfunc=lambda x: x.nunique()),
    operator=pd.NamedAgg(column="operator", aggfunc=lambda x: x.nunique()),
).reset_index()

agg = agg.astype({
    "facid": int,
    "capacity": int,
    "fac_name": int,
    "fac_address": int,
    "city_state_zip": int,
    "owner": int,
    "operator": int,
})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)