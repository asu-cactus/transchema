import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_36/training_0.csv", index_col=0)

# Identify all columns starting with "Cases_" or "Deaths_"
cases_cols = [col for col in df.columns if col.startswith("Cases_")]
deaths_cols = [col for col in df.columns if col.startswith("Deaths_")]

# Melt Cases columns
melted_cases = df.melt(id_vars=["Date", "Day"], value_vars=cases_cols, var_name="variable", value_name="value")
melted_cases = melted_cases.dropna(subset=["value"])
# Convert "Cases_Guinea" -> ['Cases', 'Guinea']
melted_cases["variable"] = melted_cases["variable"].str.split("_").apply(lambda x: str([x[0], x[1]]))

# Melt Deaths columns
melted_deaths = df.melt(id_vars=["Date", "Day"], value_vars=deaths_cols, var_name="variable", value_name="value")
melted_deaths = melted_deaths.dropna(subset=["value"])
# Convert "Deaths_Guinea" -> ['Deaths', 'Guinea']
melted_deaths["variable"] = melted_deaths["variable"].str.split("_").apply(lambda x: str([x[0], x[1]]))

# Concatenate both melted dataframes
result = pd.concat([melted_cases[["variable"]], melted_deaths[["variable"]]], ignore_index=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_36/target_multisource_mcts.csv", index=False)