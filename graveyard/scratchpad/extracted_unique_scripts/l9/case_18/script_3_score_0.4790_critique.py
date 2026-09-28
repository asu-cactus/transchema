import pandas as pd

# Read all source tables with index_col=0 to ignore the CSV index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_9.csv", index_col=0)

# Rename counts columns in business tables to match target schema
s1 = s1.rename(columns={'counts': 'counts_y'})
s3 = s3.rename(columns={'counts': 'counts_x_6'})
s7 = s7.rename(columns={'counts': 'counts_y_8'})
s9 = s9.rename(columns={'counts': 'counts_x'})

# Add business name columns with constant strings
s1['businesses_y'] = s1['businesses']
s3['businesses_x_5'] = s3['businesses']
s7['businesses_y_7'] = s7['businesses']
s9['businesses_x'] = s9['businesses']

# Drop original 'businesses' columns after copying to new columns
s1 = s1.drop(columns=['businesses'])
s3 = s3.drop(columns=['businesses'])
s7 = s7.drop(columns=['businesses'])
s9 = s9.drop(columns=['businesses'])

# Join the four business tables on zipcode
business_join_1 = pd.merge(s9, s1, on='zipcode', how='outer')
business_join_2 = pd.merge(business_join_1, s3, on='zipcode', how='outer')
business_all = pd.merge(business_join_2, s7, on='zipcode', how='outer')

# Join with s4 (boro)
joined_1 = pd.merge(business_all, s4, on='zipcode', how='left')

# Join with s6 and s8, rename counts columns accordingly
joined_2 = pd.merge(joined_1, s6.rename(columns={'counts': 'counts_x_10'}), on='zipcode', how='left')
joined_3 = pd.merge(joined_2, s8.rename(columns={'counts': 'counts_y_11'}), on='zipcode', how='left')

# Join with s0 (crime stats)
joined_4 = pd.merge(joined_3, s0, on='zipcode', how='left')

# Join with s2 (indicator and counts)
joined_5 = pd.merge(joined_4, s2.rename(columns={'counts': 'counts'}), on='zipcode', how='left')

# Join with s5 (theft, assault, harassment)
final = pd.merge(joined_5, s5, on='zipcode', how='left')

# Reorder columns to match target schema exactly
final = final[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
               'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8',
               'boro', 'counts_x_10', 'counts_y_11', 'indicator', 'counts',
               'total_crime', 'violation', 'misdemeanor', 'felony',
               'theft', 'assault', 'harassment']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv", index=False)