import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

dog_cols = ['doggo', 'floofer', 'pupper', 'puppo']
df_unpivot = df.melt(id_vars=[], value_vars=dog_cols, var_name='dog_type', value_name='flag')
df_unpivot = df_unpivot[df_unpivot['flag'].notna()]
result = df_unpivot.groupby('dog_type').size().reset_index(name='dog_type_count')

# Map dog_type to integer codes as target schema expects integer dog_type
# The target examples show integer values, so we convert dog_type categories to integer codes
result['dog_type'] = result['dog_type'].astype('category').cat.codes

# Aggregate counts by dog_type integer code
final = result.groupby('dog_type', as_index=False)['dog_type_count'].sum()
final = final.rename(columns={'dog_type_count': 'dog_type'})

final.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)