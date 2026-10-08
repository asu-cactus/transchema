import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_12/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["school_name"], value_vars=["type", "size", "budget"], var_name="variable", value_name="value")

df_joined = pd.merge(df0_unpivot, df1, on="school_name", how="inner")

result = df_joined[["school_name", "reading_score"]].copy()
result["reading_score"] = result["reading_score"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_12/target_multisource_mcts.csv", index=False)