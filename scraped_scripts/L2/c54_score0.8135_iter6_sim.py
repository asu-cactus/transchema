import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_54/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_54/training_1.csv", index_col=0)

df_union = pd.concat([df1, df2], ignore_index=True)

df_grouped = df_union.groupby("sex", as_index=False).agg({
    "Medu": "mean",
    "Fedu": "mean",
    "absences": "mean"
})

df_grouped.rename(columns={"Medu": "G1", "Fedu": "G2", "absences": "G3"}, inplace=True)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_54/target_multisource_mcts.csv", index=False)