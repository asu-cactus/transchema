import pandas as pd

# Read source tables
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_53/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_53/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_53/training_2.csv', index_col=0)

# Join Source2_53_0 and Source2_53_1 on Athlete (inner join)
join_01 = pd.merge(source0, source1, on='Athlete', how='inner')

# Join the above result with Source2_53_2 on Athlete (left join to keep all rows from join_01)
final_join = pd.merge(join_01, source2, on='Athlete', how='left')

# Group by attributes: Athlete (string), Year (int), Closing Ceremony Date (string), Country (string), Sport (string)
group_by_cols = ['Athlete', 'Year', 'Closing Ceremony Date', 'Country', 'Sport']

# Aggregations:
# Age: mean (float)
# Gold Medals, Silver Medals, Bronze Medals, Total Medals: sum (int)
agg_dict = {
    'Age': 'mean',
    'Gold Medals': 'sum',
    'Silver Medals': 'sum',
    'Bronze Medals': 'sum',
    'Total Medals': 'sum'
}

# Perform groupby and aggregation
result = final_join.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
result = result[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country', 'Sport']]

# Write to output CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length2_53/target_multisource_mcts.csv', index=False)