import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_88/training_0.csv", index_col=0)

group_cols = ['Airline', 'Date_of_Journey', 'Source', 'Destination', 'Route', 'Dep_Time', 'Arrival_Time', 'Duration', 'Total_Stops', 'Additional_Info']

agg_df = df0.groupby(group_cols).agg(
    Price_min=('Price', 'min'),
    Price_max=('Price', 'max'),
    Price_avg=('Price', 'mean')
).reset_index()

# The target schema has a single Price column (integer).
# The partial plan suggests aggregations min, max, avg on Price.
# We must produce a single Price column in the output.
# The target examples show Price as integer.
# We choose to take the average price rounded to int as the final Price.

agg_df['Price'] = agg_df['Price_avg'].round().astype(int)

# Select columns as per target schema
result = agg_df[group_cols + ['Price']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_88/target_multisource_mcts.csv", index=False)