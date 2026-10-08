import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg_df = df0.groupby("fac_type").agg(
    facid=pd.NamedAgg(column="facid", aggfunc=lambda x: x.nunique()),
    capacity=pd.NamedAgg(column="capacity", aggfunc="sum"),
    fac_name=pd.NamedAgg(column="fac_name", aggfunc=lambda x: x.nunique()),
    fac_address=pd.NamedAgg(column="fac_address", aggfunc=lambda x: x.nunique()),
    city_state_zip=pd.NamedAgg(column="city_state_zip", aggfunc=lambda x: x.nunique()),
    owner=pd.NamedAgg(column="owner", aggfunc=lambda x: x.nunique()),
    operator=pd.NamedAgg(column="operator", aggfunc=lambda x: x.nunique()),
).reset_index()

# Convert all columns except fac_type to int
for col in ["facid", "capacity", "fac_name", "fac_address", "city_state_zip", "owner", "operator"]:
    agg_df[col] = agg_df[col].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)