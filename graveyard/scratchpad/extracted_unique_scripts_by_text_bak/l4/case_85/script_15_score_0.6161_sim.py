import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

df_joined = df0.merge(df0, on="crit_cn")

df_grouped = df_joined.groupby("crit_cn", as_index=False)["critic_x"].sum()
df_grouped.rename(columns={"critic_x": "critic"}, inplace=True)
df_grouped["critic"] = pd.to_numeric(df_grouped["critic"], errors='coerce').fillna(0).astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)