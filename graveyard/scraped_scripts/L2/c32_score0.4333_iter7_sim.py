import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_32/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_32/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_32/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df1_unpivot = df1.melt(id_vars=["city"], value_vars=["driver_count", "type"], var_name="attribute", value_name="value")
df1_grouped = df1_unpivot.groupby("city", as_index=False).size()

df1_grouped = df1_grouped.rename(columns={"size": "count"})

# Join grouped df1 with df0 on city
df_joined = pd.merge(df1_grouped, df0, on="city", how="inner")

# Project only city and ride_id as target schema
result = df_joined[["city", "ride_id"]]

result.to_csv(target_path, index=False)