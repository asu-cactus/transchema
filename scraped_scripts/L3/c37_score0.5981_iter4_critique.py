import pandas as pd

# Read source files with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)  # County, r1403
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)  # County, r1402 (not needed in output)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_2.csv", index_col=0)  # County only (dimension)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)  # County, r1401

# Join df2 (dimension table with all counties) with df3 on County using left join to preserve all counties
result = pd.merge(df2, df3, on="County", how="left")

# Join with df0 on County using left join
result = pd.merge(result, df0, on="County", how="left")

# Join with df1 on County using left join (r1402 not needed in output, but must be used)
result = pd.merge(result, df1, on="County", how="left")

# Select only columns needed in target schema
result = result[["County", "r1401", "r1403"]]

# Define a helper function to get the first non-null value in a group for string columns
def first_non_null(series):
    # Return first non-null value, or 'NR' if all null (to match typical 'NR' usage)
    non_nulls = series.dropna()
    if not non_nulls.empty:
        return non_nulls.iloc[0]
    else:
        return "NR"

# Group by County to remove duplicates, aggregate r1401 and r1403 by first non-null value
result = result.groupby("County", as_index=False).agg({
    "r1401": first_non_null,
    "r1403": first_non_null
})

# Write output to target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)