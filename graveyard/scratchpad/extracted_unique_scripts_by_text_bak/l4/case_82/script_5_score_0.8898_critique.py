import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_82/training_4.csv", index_col=0)

# Join all tables on Institution
join_2_1 = pd.merge(s2, s1, on="Institution", how="inner")
join_2_1_0 = pd.merge(join_2_1, s0, on="Institution", how="inner")
join_2_1_0_3 = pd.merge(join_2_1_0, s3, on="Institution", how="inner")
final_join = pd.merge(join_2_1_0_3, s4, on="Institution", how="inner")

# Define aggregation dictionary
agg_dict = {
    '(Fall 2011)': 'mean',
    '(Fall 2012)': 'mean',
    '(Fall 2013)': 'mean',
    '(Fall 2014)': 'mean',
    'year 2014': 'sum',
    'year 2015': 'sum',
    'year 2016': 'sum',
    'Cohort 2014': 'sum',
    'Cohort 2015': 'sum',
    'Cohort 2016': 'sum'
}

# Group by Institution and aggregate accordingly
final = final_join.groupby('Institution', as_index=False).agg(agg_dict)

# Rename columns to match target schema
final.rename(columns={
    'year 2014': 'persist 2014',
    'year 2015': 'persist 2015',
    'year 2016': 'persist 2016'
}, inplace=True)

# Convert integer columns to Int64 dtype (nullable integer)
for col in ['persist 2014', 'persist 2015', 'persist 2016', 'Cohort 2014', 'Cohort 2015', 'Cohort 2016']:
    final[col] = final[col].astype('Int64')

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_82/target_multisource_mcts.csv", index=False)