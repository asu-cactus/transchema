import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_9/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_9/training_2.csv", index_col=0)

merged = pd.merge(df0, df2, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

grouped = merged.groupby("des_zona", dropna=False).agg(COD_PERSONA_x=("COD_PERSONA", "count"),
                                                      COD_AREANEGO=("cod_areanego", "first")).reset_index()

grouped["COD_PERSONA_x"] = grouped["COD_PERSONA_x"].astype(int)
grouped["COD_AREANEGO"] = grouped["COD_AREANEGO"].astype(pd.Int64Dtype())

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_9/target_multisource_mcts.csv", index=False)