import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

melted = df.melt(id_vars=[], value_vars=['doggo', 'floofer', 'pupper', 'puppo'], var_name='dog_type', value_name='flag')
filtered = melted[melted['flag'].notna()]
result = filtered.groupby('dog_type').size().reset_index(name='dog_type_count')

# Map dog_type strings to integers as in target examples:
# The target examples show dog_type as integers: 4471, 30, 8 etc.
# But the source columns are categorical strings: doggo, floofer, pupper, puppo.
# The target schema is ['dog_type': integer], and the example values are counts.
# So the target is the count per dog_type category, but dog_type is integer in target.
# The partial plan says UNPIVOT then GROUP_BY dog_type.
# The target examples show counts, so dog_type column is the count.
# So the target table has a single column dog_type which is the count of all dog types combined.
# But the example shows multiple rows with dog_type values 4471, 30, 8, which likely correspond to counts per dog type.
# So the target dog_type column is the count per dog type category.
# So we rename the count column to dog_type and drop the dog_type string column.

result = result.rename(columns={'dog_type_count': 'dog_type'})
result = result[['dog_type']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)