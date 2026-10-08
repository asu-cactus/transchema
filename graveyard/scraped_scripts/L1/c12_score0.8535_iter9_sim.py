import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_1.csv", index_col=0)

grouped = df0.groupby(['Athlete', 'Year', 'Closing Ceremony Date', 'Age'], dropna=False).agg({
    'Gold Medals': 'sum',
    'Silver Medals': 'sum',
    'Bronze Medals': 'sum',
    'Total Medals': 'sum'
}).reset_index()

merged = pd.merge(grouped, df1, on='Athlete', how='left')

merged['Age'] = merged['Age'].astype(float)
merged['Year'] = merged['Year'].astype(int)
merged['Gold Medals'] = merged['Gold Medals'].fillna(0).astype(int)
merged['Silver Medals'] = merged['Silver Medals'].fillna(0).astype(int)
merged['Bronze Medals'] = merged['Bronze Medals'].fillna(0).astype(int)
merged['Total Medals'] = merged['Total Medals'].fillna(0).astype(int)
merged['Closing Ceremony Date'] = merged['Closing Ceremony Date'].astype(str)
merged['Country'] = merged['Country'].astype(str)

merged = merged[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts.csv", index=False)