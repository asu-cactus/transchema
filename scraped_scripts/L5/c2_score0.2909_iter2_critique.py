import pandas as pd

# Load sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

# Aggregate counts by zipcode and businesses for each source with counts
agg0 = source0.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()
agg2 = source2.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()
agg3 = source3.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()
agg4 = source4.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()

# Rename counts columns to distinguish sources according to target schema
agg0 = agg0.rename(columns={'businesses': 'businesses_x_5', 'counts': 'counts_x_6'})
agg2 = agg2.rename(columns={'businesses': 'businesses_y', 'counts': 'counts_y'})
agg3 = agg3.rename(columns={'businesses': 'businesses_y_7', 'counts': 'counts_y_8'})
agg4 = agg4.rename(columns={'businesses': 'businesses_x', 'counts': 'counts_x'})

# Join all aggregated sources on zipcode and business names where applicable
# Since business columns differ, we join on zipcode only and keep all business/count columns separately

# First, merge agg4 and agg2 on zipcode (outer join to keep all zipcodes)
df = pd.merge(agg4, agg2, on='zipcode', how='outer')

# Merge agg0 (Debt Collection Agency) on zipcode
df = pd.merge(df, agg0, on='zipcode', how='outer')

# Merge agg3 (Cigarette Retail Dealer) on zipcode
df = pd.merge(df, agg3, on='zipcode', how='outer')

# Now, for each business/count pair, keep only rows where business matches the expected business name from target schema
# Because each source has only one business type per row, we can filter rows accordingly and then pivot counts per zipcode

# For businesses_x (Sidewalk Cafe) from agg4
sidewalk_cafe = df[df['businesses_x'] == 'Sidewalk Cafe'][['zipcode', 'businesses_x', 'counts_x']]

# For businesses_y (Pawnbroker) from agg2
pawnbroker = df[df['businesses_y'] == 'Pawnbroker'][['zipcode', 'businesses_y', 'counts_y']]

# For businesses_x_5 (Debt Collection Agency) from agg0
debt_collection = df[df['businesses_x_5'] == 'Debt Collection Agency'][['zipcode', 'businesses_x_5', 'counts_x_6']]

# For businesses_y_7 (Cigarette Retail Dealer) from agg3
cigarette = df[df['businesses_y_7'] == 'Cigarette Retail Dealer'][['zipcode', 'businesses_y_7', 'counts_y_8']]

# Merge all these on zipcode to get one row per zipcode with all business/count columns
df_final = pd.DataFrame({'zipcode': pd.unique(df['zipcode'])})

df_final = df_final.merge(sidewalk_cafe[['zipcode', 'businesses_x', 'counts_x']], on='zipcode', how='left')
df_final = df_final.merge(pawnbroker[['zipcode', 'businesses_y', 'counts_y']], on='zipcode', how='left')
df_final = df_final.merge(debt_collection[['zipcode', 'businesses_x_5', 'counts_x_6']], on='zipcode', how='left')
df_final = df_final.merge(cigarette[['zipcode', 'businesses_y_7', 'counts_y_8']], on='zipcode', how='left')

# Join with source1 to get boro
df_final = df_final.merge(source1, on='zipcode', how='left')

# Join with source5 to get businesses (integer)
df_final = df_final.merge(source5, on='zipcode', how='left')

# Fill NaN counts with 0 and convert to int
for col in ['counts_x', 'counts_y', 'counts_x_6', 'counts_y_8']:
    if col in df_final.columns:
        df_final[col] = df_final[col].fillna(0).astype(int)

# The target schema columns order:
# ['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']

# Ensure all columns exist, fill missing with NaN
for col in ['businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']:
    if col not in df_final.columns:
        df_final[col] = pd.NA

df_final = df_final[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
                     'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8',
                     'boro', 'businesses']]

# Group by zipcode and aggregate counts and businesses columns as needed
# For business name columns, take first non-null (since they are constant per zipcode)
# For counts columns and 'businesses' (integer from source5), sum them

agg_dict = {
    'businesses_x': 'first',
    'counts_x': 'sum',
    'businesses_y': 'first',
    'counts_y': 'sum',
    'businesses_x_5': 'first',
    'counts_x_6': 'sum',
    'businesses_y_7': 'first',
    'counts_y_8': 'sum',
    'boro': 'first',
    'businesses': 'sum'
}

df_final = df_final.groupby('zipcode', as_index=False).agg(agg_dict)

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)