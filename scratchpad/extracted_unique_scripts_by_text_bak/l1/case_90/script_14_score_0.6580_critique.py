import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

dog_cols = ['doggo', 'floofer', 'pupper', 'puppo']

# Unpivot dog type columns
df_unpivot = df.melt(id_vars=[], value_vars=dog_cols, var_name='dog_type', value_name='flag')

# Filter rows where flag is not null
df_unpivot = df_unpivot[df_unpivot['flag'].notna()]

# Map dog_type strings to integer codes
df_unpivot['dog_type'] = df_unpivot['dog_type'].astype('category').cat.codes

# Group by dog_type integer code and count occurrences
result = df_unpivot.groupby('dog_type', as_index=False).size()

# Rename count column to 'dog_type' as per target schema
result.columns = ['dog_type', 'dog_type_count']
final = result.rename(columns={'dog_type_count': 'dog_type'})

final.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)