import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_3.csv", index_col=0)

# Add Year column to each source according to their order
s0['Year'] = 2013
s1['Year'] = 2014
s2['Year'] = 2015
s3['Year'] = 2016

# Union all source tables vertically
df_union = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Pivot the data to get columns like '2013 Wins', '2013 Losses', etc.
df_pivot = df_union.pivot(index='Wrestler', columns='Year', values=['Wins', 'Losses', 'Draws'])

# Flatten MultiIndex columns and rename to match target schema
df_pivot.columns = [f"{year} {stat}" for stat, year in df_pivot.columns]

# Reset index to bring Wrestler back as a column
df_final = df_pivot.reset_index()

# Reorder columns to match target schema exactly
target_columns = ['Wrestler',
                  '2013 Wins', '2013 Losses', '2013 Draws',
                  '2014 Wins', '2014 Losses', '2014 Draws',
                  '2015 Wins', '2015 Losses', '2015 Draws',
                  '2016 Wins', '2016 Losses', '2016 Draws']

# Some wrestlers may not have data for all years, so columns may have NaNs; keep as is
df_final = df_final[target_columns]

# Write to CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_1/target_multisource_mcts.csv", index=False)