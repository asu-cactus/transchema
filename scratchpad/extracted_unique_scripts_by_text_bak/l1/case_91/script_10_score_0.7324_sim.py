import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

group_cols = ['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season']

agg_df = df.groupby(group_cols).agg({
    'Name': 'count',
    'Transfer_fee': 'min',
    'Market_value': 'min'
}).rename(columns={'Name': 'Name_count', 'Transfer_fee': 'Transfer_fee', 'Market_value': 'Market_value'}).reset_index()

# The target schema requires:
# Name (string), Position (string), Age (int), Team_from (string), League_from (string),
# Team_to (string), League_to (string), Season (string), Market_value (float), Transfer_fee (int)

# Since the aggregation on Name is count, but target expects Name as string, we must keep the original Name.
# The aggregation count(Name) is not needed in final output, so we discard it.

# The aggregation MIN(Transfer_fee) and MIN(Market_value) are used to get one value per group.

# So we just keep the grouped columns and the aggregated Transfer_fee and Market_value.

# Convert Age to int, Transfer_fee to int, Market_value to float (already float but ensure)
agg_df['Age'] = agg_df['Age'].astype(int)
agg_df['Transfer_fee'] = agg_df['Transfer_fee'].astype('Int64')  # allow NA integers
agg_df['Market_value'] = agg_df['Market_value'].astype(float)

# Drop the count column 'Name_count' as it's not part of target schema
agg_df = agg_df.drop(columns=['Name_count'])

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)