import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_0.csv", index_col=0)  # mixed_population
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_1.csv", index_col=0)  # whites_population
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_2.csv", index_col=0)  # other_population
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_54/training_3.csv", index_col=0)  # black_population

# Start join from Source2 (other_population) to preserve all rows in Source2
r0 = pd.merge(df2, df1, on=["CountyID", "CountyName", "Year", "ID"], how="left", suffixes=('_y', '_x'))
# r0 columns: CountyID, CountyName, other_population, Year, ID, whites_population

# Join with Source0 (mixed_population)
r1 = pd.merge(r0, df0, on=["CountyID", "CountyName", "Year", "ID"], how="left", suffixes=('', '_x_10'))
# r1 columns: CountyID, CountyName, other_population, Year, ID, whites_population, mixed_population

# Join with Source3 (black_population)
r2 = pd.merge(r1, df3, on=["CountyID", "CountyName", "Year", "ID"], how="left", suffixes=('', '_y_14'))
# r2 columns: CountyID, CountyName, other_population, Year, ID, whites_population, mixed_population, black_population

# Now rename columns to match target schema exactly, including repeated keys with suffixes
result = pd.DataFrame()

# According to target schema and examples, assign columns as follows:
# Source1 (whites_population) keys: CountyID_x, CountyName_x, Year_x, ID
result["CountyID_x"] = r2["CountyID"]
result["CountyName_x"] = r2["CountyName"]
result["whites_population"] = r2["whites_population"]
result["Year_x"] = r2["Year"]
result["ID"] = r2["ID"]

# Source2 (other_population) keys: CountyID_y, CountyName_y, Year_y
result["CountyID_y"] = r2["CountyID"]
result["CountyName_y"] = r2["CountyName"]
result["other_population"] = r2["other_population"]
result["Year_y"] = r2["Year"]

# Source0 (mixed_population) keys: CountyID_x_9, CountyName_x_10, Year_x_12
result["CountyID_x_9"] = r2["CountyID"]
result["CountyName_x_10"] = r2["CountyName"]
result["mixed_population"] = r2["mixed_population"]
result["Year_x_12"] = r2["Year"]

# Source3 (black_population) keys: CountyID_y_13, CountyName_y_14, Year_y_16
result["CountyID_y_13"] = r2["CountyID"]
result["CountyName_y_14"] = r2["CountyName"]
result["black_population"] = r2["black_population"]
result["Year_y_16"] = r2["Year"]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_54/target_multisource_mcts.csv", index=False)