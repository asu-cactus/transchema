import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_1.csv", index_col=0)

# Join on Athlete
merged = pd.merge(df0, df1, on='Athlete', how='left')

# Group by Athlete, Year, Closing Ceremony Date
grouped = merged.groupby(['Athlete', 'Year', 'Closing Ceremony Date'], as_index=False).agg({
    'Age': 'mean',
    'Gold Medals': 'sum',
    'Silver Medals': 'sum',
    'Bronze Medals': 'sum',
    'Total Medals': 'sum',
    'Country': 'first'  # Country is constant per athlete, so take first
})

# Reorder columns to match target schema
result = grouped[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts.csv", index=False)