import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_12/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_12/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on Athlete (left join to keep all medal records)
merged = pd.merge(df0, df1, on='Athlete', how='left')

# Group by Athlete and Year
agg = merged.groupby(['Athlete', 'Year'], dropna=False).agg({
    'Age': 'mean',
    'Closing Ceremony Date': 'first',
    'Gold Medals': 'sum',
    'Silver Medals': 'sum',
    'Bronze Medals': 'sum'
}).reset_index()

# Compute Total Medals as sum of medal counts
agg['Total Medals'] = agg['Gold Medals'] + agg['Silver Medals'] + agg['Bronze Medals']

# Add Country column by merging again to get Country (Country is constant per Athlete)
# Since Country is constant per Athlete, we can get it from df1 by dropping duplicates
country = df1.drop_duplicates(subset=['Athlete'])[['Athlete', 'Country']]
agg = pd.merge(agg, country, on='Athlete', how='left')

# Reorder columns as per target schema
result = agg[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country']]

# Cast columns to correct types
result['Age'] = result['Age'].astype(float)
result['Year'] = result['Year'].astype(int)
result['Gold Medals'] = result['Gold Medals'].astype(int)
result['Silver Medals'] = result['Silver Medals'].astype(int)
result['Bronze Medals'] = result['Bronze Medals'].astype(int)
result['Total Medals'] = result['Total Medals'].astype(int)
result['Closing Ceremony Date'] = result['Closing Ceremony Date'].astype(str)
result['Country'] = result['Country'].astype(str)

result.to_csv(target_path, index=False)