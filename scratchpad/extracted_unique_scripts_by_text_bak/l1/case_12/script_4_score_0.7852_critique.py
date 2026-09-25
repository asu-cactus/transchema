import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_1.csv", index_col=0)

# Join on Athlete with inner join to keep only athletes present in both tables
result = pd.merge(df0, df1, on="Athlete", how="inner")

# Reorder columns to match target schema
result = result[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country']]

# Cast columns to correct types
result['Age'] = result['Age'].astype(float)
result['Year'] = result['Year'].astype('Int64')
result['Gold Medals'] = result['Gold Medals'].astype('Int64')
result['Silver Medals'] = result['Silver Medals'].astype('Int64')
result['Bronze Medals'] = result['Bronze Medals'].astype('Int64')
result['Total Medals'] = result['Total Medals'].astype('Int64')
result['Closing Ceremony Date'] = result['Closing Ceremony Date'].astype(str)
result['Country'] = result['Country'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts.csv", index=False)