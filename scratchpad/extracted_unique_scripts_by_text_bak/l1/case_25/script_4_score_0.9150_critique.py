import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_1.csv", index_col=0)

# Rename columns in df1 to avoid suffixes after join
# But since we will rename after join, no need to rename here

# Join on 'State' with inner join to keep only matching states
df = pd.merge(df0, df1, on="State", how="inner", suffixes=('_x', '_y'))

# Group by 'State' to ensure uniqueness
# Define aggregation dictionary:
agg_dict = {
    'Participation_x': 'first',
    'English': 'mean',
    'Math_x': 'mean',
    'Reading': 'mean',
    'Science': 'mean',
    'Composite': 'mean',
    'Participation_y': 'first',
    'Evidence-Based Reading and Writing': 'first',
    'Math_y': 'first',
    'Total': 'first'
}

df_grouped = df.groupby('State', as_index=False).agg(agg_dict)

# Cast integer columns to int
df_grouped['Evidence-Based Reading and Writing'] = df_grouped['Evidence-Based Reading and Writing'].astype('Int64')
df_grouped['Math_y'] = df_grouped['Math_y'].astype('Int64')
df_grouped['Total'] = df_grouped['Total'].astype('Int64')

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                         'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts.csv", index=False)