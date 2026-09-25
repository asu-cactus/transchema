import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

# Join on city
df_joined = source0.merge(source1, on='city', how='inner')

# Group by city and aggregate
agg_df = df_joined.groupby('city').agg(
    **{
        'Average Fare ($)': ('fare', 'mean'),
        'Number of Rides': ('ride_id', 'count'),
        'Number of Drivers': ('driver_count', 'sum'),
        'City Type': ('type', 'first')
    }
).reset_index()

# Rename city to City to match target schema
agg_df.rename(columns={'city': 'City'}, inplace=True)

# Ensure Number of Drivers is integer type
agg_df['Number of Drivers'] = agg_df['Number of Drivers'].astype('Int64')

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)