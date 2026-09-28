import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_14/training_3.csv", index_col=0)

# Join Source4_14_0 and Source4_14_3 on COD_PERSONA
df_0_3 = pd.merge(df0, df3, on="COD_PERSONA", how="inner", suffixes=('_0', '_3'))

# Join the above with Source4_14_1 on COD_IDCONTRA and COD_PERSONA
df_0_3_1 = pd.merge(df_0_3, df1, on=["COD_IDCONTRA", "COD_PERSONA"], how="inner", suffixes=('', '_1'))

# Join the above with Source4_14_2 on COD_OFICIPAL (from df_0_3_1) and COD_OFICI (from df2)
df_final = pd.merge(df_0_3_1, df2, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner", suffixes=('', '_2'))

# Select only the target columns
df_target = df_final[["COD_INTERV", "estado_cli", "COD_EDAD", "COD_OFICIPAL", "COD_SEGLOBAL"]]

# Fix data types according to target schema
df_target = df_target.astype({
    "COD_INTERV": "string",
    "estado_cli": "string",
    "COD_EDAD": "Int64",
    "COD_OFICIPAL": "Int64",
    "COD_SEGLOBAL": "Int64"
})

# Group by all target columns to remove duplicates (no aggregation)
df_target = df_target.drop_duplicates()

# Write to output
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length4_14/target_multisource_mcts.csv", index=False)