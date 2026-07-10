import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

# Filter each business type from the respective source tables and rename columns to match target schema

# From Source5_2_4: Sidewalk Cafe -> businesses_x, counts_x
sidewalk = df4[df4['businesses'] == 'Sidewalk Cafe'][['zipcode', 'counts']].rename(columns={'counts': 'counts_x'})
sidewalk['businesses_x'] = 'Sidewalk Cafe'

# From Source5_2_2: Pawnbroker -> businesses_y, counts_y
pawnbroker = df2[df2['businesses'] == 'Pawnbroker'][['zipcode', 'counts']].rename(columns={'counts': 'counts_y'})
pawnbroker['businesses_y'] = 'Pawnbroker'

# From Source5_2_0: Debt Collection Agency -> businesses_x_5, counts_x_6
debt_collection = df0[df0['businesses'] == 'Debt Collection Agency'][['zipcode', 'counts']].rename(columns={'counts': 'counts_x_6'})
debt_collection['businesses_x_5'] = 'Debt Collection Agency'

# From Source5_2_3: Cigarette Retail Dealer -> businesses_y_7, counts_y_8
cigarette = df3[df3['businesses'] == 'Cigarette Retail Dealer'][['zipcode', 'counts']].rename(columns={'counts': 'counts_y_8'})
cigarette['businesses_y_7'] = 'Cigarette Retail Dealer'

# Join all filtered business tables on zipcode using outer joins to keep all zipcodes
join_1 = pd.merge(sidewalk, pawnbroker, on='zipcode', how='outer')
join_2 = pd.merge(join_1, debt_collection, on='zipcode', how='outer')
join_3 = pd.merge(join_2, cigarette, on='zipcode', how='outer')

# Join with Source5_2_1 (boro, zipcode)
join_4 = pd.merge(join_3, df1, on='zipcode', how='outer')

# Join with Source5_2_5 (zipcode, businesses) - businesses is integer count
join_5 = pd.merge(join_4, df5, on='zipcode', how='outer')

# Group by zipcode to ensure unique rows and aggregate businesses (sum)
final = join_5.groupby('zipcode', as_index=False).agg({
    'businesses_x': 'first',
    'counts_x': 'first',
    'businesses_y': 'first',
    'counts_y': 'first',
    'businesses_x_5': 'first',
    'counts_x_6': 'first',
    'businesses_y_7': 'first',
    'counts_y_8': 'first',
    'boro': 'first',
    'businesses': 'sum'
})

# Reorder columns to match target schema exactly
final = final[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
               'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']]

# Write to output CSV
final.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)