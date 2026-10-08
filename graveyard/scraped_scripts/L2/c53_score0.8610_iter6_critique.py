import pandas as pd

# Read source tables
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_53/training_0.csv', index_col=0)  # Source2_53_0
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_53/training_1.csv', index_col=0)  # Source2_53_1
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_53/training_2.csv', index_col=0)  # Source2_53_2

# Join Source2_53_1 and Source2_53_2 on Athlete to add Country
df = pd.merge(source1, source2, on='Athlete', how='inner')

# Join the above result with Source2_53_0 on Athlete to add Sport
df = pd.merge(df, source0, on='Athlete', how='inner')

# Group by Athlete and Year to ensure uniqueness and aggregate as needed
agg_dict = {
    'Age': 'first',
    'Closing Ceremony Date': 'first',
    'Gold Medals': 'sum',
    'Silver Medals': 'sum',
    'Bronze Medals': 'sum',
    'Total Medals': 'sum',
    'Country': 'first',
    'Sport': 'first'
}

df = df.groupby(['Athlete', 'Year'], as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
df = df[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country', 'Sport']]

# Write output
df.to_csv('autopipeline-benchmarks/github-pipelines/length2_53/target_multisource_mcts.csv', index=False)