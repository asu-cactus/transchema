import pandas as pd

# Read all sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_2.csv", index_col=0)

# Join Source3_87_1 and Source3_87_2 on 'Country'
df1_2 = pd.merge(df1, df2, on="Country", how="inner")

# Join the above with Source3_87_0 on df1_2.Country = df0['Country Name']
df_all = pd.merge(df1_2, df0, left_on="Country", right_on="Country Name", how="inner")

# Group by 'Rank' and count rows per Rank
result = df_all.groupby("Rank").size().reset_index(name='0')

# Ensure types match target schema
result['Rank'] = result['Rank'].astype(int)
result['0'] = result['0'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_87/target_multisource_mcts.csv", index=False)