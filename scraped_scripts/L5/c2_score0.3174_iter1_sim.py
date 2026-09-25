import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

union = pd.concat([src0, src2, src3, src4], ignore_index=True)

joined_0 = pd.merge(union, src1, on="zipcode", how="left")

final = pd.merge(joined_0, src5, on="zipcode", how="left")

# Now we have columns:
# zipcode, businesses_x, counts_x, boro, businesses_y
# We need to produce the target schema:
# ['zipcode': int, 'businesses_x': str, 'counts_x': int, 'businesses_y': str, 'counts_y': int,
#  'businesses_x_5': str, 'counts_x_6': int, 'businesses_y_7': str, 'counts_y_8': int,
#  'boro': str, 'businesses': int]

# The union combined 4 sources with schema (zipcode, businesses, counts)
# After union, businesses and counts columns are ambiguous for different business types.
# The target schema has 4 pairs of business/count columns plus boro and businesses (int).

# We need to pivot or separate the unioned data into 4 business/count pairs:
# From the target examples and source names, likely:
# businesses_x, counts_x: Sidewalk Cafe (from Source5_2_4)
# businesses_y, counts_y: Pawnbroker (from Source5_2_2)
# businesses_x_5, counts_x_6: Debt Collection Agency (from Source5_2_0)
# businesses_y_7, counts_y_8: Cigarette Retail Dealer (from Source5_2_3)

# So we split union into 4 dataframes by business type, rename columns accordingly, then join on zipcode.

# Extract each business type from union:
sidewalk = union[union['businesses'] == 'Sidewalk Cafe'][['zipcode', 'businesses', 'counts']].rename(
    columns={'businesses': 'businesses_x', 'counts': 'counts_x'})
pawnbroker = union[union['businesses'] == 'Pawnbroker'][['zipcode', 'businesses', 'counts']].rename(
    columns={'businesses': 'businesses_y', 'counts': 'counts_y'})
debt = union[union['businesses'] == 'Debt Collection Agency'][['zipcode', 'businesses', 'counts']].rename(
    columns={'businesses': 'businesses_x_5', 'counts': 'counts_x_6'})
cigarette = union[union['businesses'] == 'Cigarette Retail Dealer'][['zipcode', 'businesses', 'counts']].rename(
    columns={'businesses': 'businesses_y_7', 'counts': 'counts_y_8'})

# Merge these on zipcode (outer join to keep all zipcodes)
df = pd.merge(sidewalk, pawnbroker, on='zipcode', how='outer')
df = pd.merge(df, debt, on='zipcode', how='outer')
df = pd.merge(df, cigarette, on='zipcode', how='outer')

# Add boro from src1 (zipcode, boro)
df = pd.merge(df, src1, on='zipcode', how='left')

# Add businesses (int) from src5 (zipcode, businesses)
df = pd.merge(df, src5.rename(columns={'businesses': 'businesses'}), on='zipcode', how='left')

# Ensure correct dtypes
df['zipcode'] = df['zipcode'].astype(int)
df['counts_x'] = pd.to_numeric(df['counts_x'], errors='coerce').fillna(0).astype(int)
df['counts_y'] = pd.to_numeric(df['counts_y'], errors='coerce').fillna(0).astype(int)
df['counts_x_6'] = pd.to_numeric(df['counts_x_6'], errors='coerce').fillna(0).astype(int)
df['counts_y_8'] = pd.to_numeric(df['counts_y_8'], errors='coerce').fillna(0).astype(int)
df['businesses_x'] = df['businesses_x'].astype('string')
df['businesses_y'] = df['businesses_y'].astype('string')
df['businesses_x_5'] = df['businesses_x_5'].astype('string')
df['businesses_y_7'] = df['businesses_y_7'].astype('string')
df['boro'] = df['boro'].astype('string')
df['businesses'] = pd.to_numeric(df['businesses'], errors='coerce').fillna(0).astype(int)

df = df[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
         'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)