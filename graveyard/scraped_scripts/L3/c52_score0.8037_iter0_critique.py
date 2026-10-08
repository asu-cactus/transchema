import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv", index_col=0)

# For each source, aggregate counts by zipcode and businesses, then pick top business per zipcode
def top_business_per_zip(df, business_col_name, counts_col_name):
    agg = df.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()
    agg = agg.sort_values(['zipcode', 'counts'], ascending=[True, False])
    top = agg.groupby('zipcode').head(1)
    top = top.rename(columns={'businesses': business_col_name, 'counts': counts_col_name})
    return top

agg_0 = top_business_per_zip(df0, 'businesses_x', 'counts_x')
agg_1 = top_business_per_zip(df1, 'businesses_y', 'counts_y')
agg_2 = top_business_per_zip(df2, 'businesses_x_5', 'counts_x_6')
agg_3 = top_business_per_zip(df3, 'businesses_y_7', 'counts_y_8')

# Join all on zipcode using inner join to keep only zipcodes present in all sources
result = agg_0.merge(agg_1, on='zipcode', how='inner') \
              .merge(agg_2, on='zipcode', how='inner') \
              .merge(agg_3, on='zipcode', how='inner')

# Ensure correct dtypes as per target schema
result = result.astype({
    'zipcode': 'int64',
    'businesses_x': 'string',
    'counts_x': 'Int64',
    'businesses_y': 'string',
    'counts_y': 'Int64',
    'businesses_x_5': 'string',
    'counts_x_6': 'Int64',
    'businesses_y_7': 'string',
    'counts_y_8': 'Int64'
})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv", index=False)