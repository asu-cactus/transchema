import pandas as pd

# Read source tables
source0_path = "autopipeline-benchmarks/github-pipelines/length1_64/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_64/training_1.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on name = hero_names
df_joined = pd.merge(df0, df1, left_on='name', right_on='hero_names', how='inner')

# Define group by columns (leftmost non-float unique columns from target schema)
group_by_cols = ['name', 'Gender', 'Eye color', 'Race', 'Hair color', 'Height', 'Publisher', 'Skin color', 'Alignment']

# Weight is float, aggregate by mean
# hero_names: string, aggregate by first (all same per group)
# Boolean columns: aggregate by max (logical OR)

# List all boolean columns from df1 except hero_names
bool_cols = df1.columns.drop('hero_names').tolist()

# Aggregations dictionary
agg_dict = {'Weight': 'mean', 'hero_names': 'first'}
agg_dict.update({col: 'max' for col in bool_cols})

# Group by and aggregate
df_final = df_joined.groupby(group_by_cols).agg(agg_dict).reset_index()

# Reorder columns to match target schema exactly
# Target schema columns:
target_columns = ['name', 'Gender', 'Eye color', 'Race', 'Hair color', 'Height', 'Publisher', 'Skin color', 'Alignment', 'Weight'] + \
                 ['hero_names'] + bool_cols

df_final = df_final[target_columns]

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_64/target_multisource_mcts.csv", index=False)