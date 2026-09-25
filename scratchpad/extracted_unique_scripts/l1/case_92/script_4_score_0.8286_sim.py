import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)

agg_df = df0.groupby("user_id").agg(
    email_count=pd.NamedAgg(column="email", aggfunc="count"),
    geo_count_distinct=pd.NamedAgg(column="geo", aggfunc=lambda x: x.nunique())
).reset_index()

agg_df["email"] = agg_df["email_count"].astype(str)
agg_df["geo"] = agg_df["geo_count_distinct"].astype(str)

result = agg_df[["user_id", "email", "geo"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)