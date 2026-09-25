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

# Pivot each aggregated source to have businesses as columns and counts as values
pivot0 = agg0.pivot(index='zipcode', columns='businesses', values='counts').add_prefix('counts_x_')
pivot2 = agg2.pivot(index='zipcode', columns='businesses', values='counts').add_prefix('counts_y_')
pivot3 = agg3.pivot(index='zipcode', columns='businesses', values='counts').add_prefix('counts_y_')
pivot4 = agg4.pivot(index='zipcode', columns='businesses', values='counts').add_prefix('counts_x_')

# Also keep the business names for columns (to match target schema)
# From target schema and examples, businesses_x = Sidewalk Cafe, businesses_y = Pawnbroker,
# businesses_x_5 = Debt Collection Agency, businesses_y_7 = Cigarette Retail Dealer
# We need to map these business names to columns accordingly.

# Extract the business names from each source for the pivot columns
# We will rename columns to match target schema:
# From source4 (Sidewalk Cafe) -> businesses_x, counts_x
# From source2 (Pawnbroker) -> businesses_y, counts_y
# From source0 (Debt Collection Agency) -> businesses_x_5, counts_x_6
# From source3 (Cigarette Retail Dealer) -> businesses_y_7, counts_y_8

# For source4 (Sidewalk Cafe)
sidewalk_cafe_counts = pivot4.get('counts_x_Sidewalk Cafe', pd.Series(dtype='float')).rename('counts_x')
sidewalk_cafe_business = pd.Series(['Sidewalk Cafe'] * len(sidewalk_cafe_counts), index=sidewalk_cafe_counts.index, name='businesses_x')

# For source2 (Pawnbroker)
pawnbroker_counts = pivot2.get('counts_y_Pawnbroker', pd.Series(dtype='float')).rename('counts_y')
pawnbroker_business = pd.Series(['Pawnbroker'] * len(pawnbroker_counts), index=pawnbroker_counts.index, name='businesses_y')

# For source0 (Debt Collection Agency)
debt_collection_counts = pivot0.get('counts_x_Debt Collection Agency', pd.Series(dtype='float')).rename('counts_x_6')
debt_collection_business = pd.Series(['Debt Collection Agency'] * len(debt_collection_counts), index=debt_collection_counts.index, name='businesses_x_5')

# For source3 (Cigarette Retail Dealer)
cigarette_counts = pivot3.get('counts_y_Cigarette Retail Dealer', pd.Series(dtype='float')).rename('counts_y_8')
cigarette_business = pd.Series(['Cigarette Retail Dealer'] * len(cigarette_counts), index=cigarette_counts.index, name='businesses_y_7')

# Combine all into one DataFrame indexed by zipcode
df = pd.DataFrame(index=source1['zipcode'].unique())
df.index.name = 'zipcode'

df = df.join(sidewalk_cafe_business).join(sidewalk_cafe_counts)
df = df.join(pawnbroker_business).join(pawnbroker_counts)
df = df.join(debt_collection_business).join(debt_collection_counts)
df = df.join(cigarette_business).join(cigarette_counts)

# Reset index to have zipcode as a column
df = df.reset_index()

# Join with source1 to get boro
df = df.merge(source1, on='zipcode', how='left')

# Join with source5 to get businesses (integer)
df = df.merge(source5, on='zipcode', how='left')

# Convert counts columns to integer, fill NaN with 0 before conversion
for col in ['counts_x', 'counts_y', 'counts_x_6', 'counts_y_8']:
    if col in df.columns:
        df[col] = df[col].fillna(0).astype(int)

# The target schema columns order:
# ['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']

# Ensure all columns exist, fill missing with NaN or appropriate default
for col in ['businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']:
    if col not in df.columns:
        df[col] = pd.NA

df = df[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)