import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_56/training_3.csv", index_col=0)

agg1 = df1.groupby("CountyName", as_index=False).agg({
    "asian_population": "sum"
})
agg2 = df2.groupby("CountyName", as_index=False).agg({
    "other_population": "sum"
})
agg3 = df3.groupby("CountyName", as_index=False).agg({
    "mixed_population": "sum"
})
agg0 = df0.groupby("CountyName", as_index=False).agg({
    "whites_population": "sum"
})

# Merge all aggregated data on CountyName
merged = agg0.merge(agg1, on="CountyName", how="outer")
merged = merged.merge(agg2, on="CountyName", how="outer")
merged = merged.merge(agg3, on="CountyName", how="outer")

# Now join back with original dfs on CountyName to get all other columns
# We join df0, df1, df2, df3 on CountyName, Year, ID, CountyID to get all columns for target

# First join df0 and df1 on CountyID, CountyName, Year, ID
df01 = pd.merge(df0, df1, on=["CountyID", "CountyName", "Year", "ID"], suffixes=('_x', '_y'), how='outer')
# Then join df01 with df2
df012 = pd.merge(df01, df2, on=["CountyID", "CountyName", "Year", "ID"], how='outer', suffixes=('', '_y2'))
# Then join df012 with df3
df0123 = pd.merge(df012, df3, on=["CountyID", "CountyName", "Year", "ID"], how='outer', suffixes=('', '_y3'))

# Now rename columns to match target schema
# Target columns:
# ['CountyID_x', 'CountyName_x', 'whites_population', 'Year_x', 'ID',
#  'CountyID_y', 'CountyName_y', 'other_population', 'Year_y',
#  'CountyID_x_9', 'CountyName_x_10', 'mixed_population', 'Year_x_12',
#  'CountyID_y_13', 'CountyName_y_14', 'asian_population', 'Year_y_16']

# The joins created columns with suffixes _x, _y, and some without suffixes.
# We need to create these columns accordingly.

# Create columns for whites_population from df0 (original df0 whites_population)
df0123["whites_population"] = df0123["whites_population"]

# other_population from df2 (no suffix)
df0123["other_population"] = df0123["other_population"]

# mixed_population from df3 (no suffix)
df0123["mixed_population"] = df0123["mixed_population"]

# asian_population from df1 (with suffix _y)
df0123["asian_population"] = df0123["asian_population"]

# Now create the multiple CountyID and CountyName columns with suffixes as in target

df0123["CountyID_x"] = df0123["CountyID"]
df0123["CountyName_x"] = df0123["CountyName"]
df0123["Year_x"] = df0123["Year"]

df0123["ID"] = df0123["ID"]

df0123["CountyID_y"] = df0123["CountyID"]
df0123["CountyName_y"] = df0123["CountyName"]
df0123["Year_y"] = df0123["Year"]

df0123["CountyID_x_9"] = df0123["CountyID"]
df0123["CountyName_x_10"] = df0123["CountyName"]
df0123["Year_x_12"] = df0123["Year"]

df0123["CountyID_y_13"] = df0123["CountyID"]
df0123["CountyName_y_14"] = df0123["CountyName"]
df0123["Year_y_16"] = df0123["Year"]

# Select columns in the exact order of target schema
result = df0123[[
    "CountyID_x", "CountyName_x", "whites_population", "Year_x", "ID",
    "CountyID_y", "CountyName_y", "other_population", "Year_y",
    "CountyID_x_9", "CountyName_x_10", "mixed_population", "Year_x_12",
    "CountyID_y_13", "CountyName_y_14", "asian_population", "Year_y_16"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_56/target_multisource_mcts.csv", index=False)