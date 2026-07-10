import pandas as pd

# Read the single source table (if more existed, read and union them)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

# If multiple source tables existed, union them here:
# df = pd.concat([df0, df1, df2, ...], ignore_index=True)

# Group by CUSTOMERNAME and count ORDERNUMBER
df_grouped = df0.groupby("CUSTOMERNAME", as_index=False)["ORDERNUMBER"].count()

# Rename the count column to ORDERNUMBER as per target schema
df_grouped = df_grouped.rename(columns={"ORDERNUMBER": "ORDERNUMBER"})

# Ensure ORDERNUMBER is integer type
df_grouped["ORDERNUMBER"] = df_grouped["ORDERNUMBER"].astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)