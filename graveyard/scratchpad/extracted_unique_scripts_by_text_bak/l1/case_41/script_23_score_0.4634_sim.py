import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

melted = df.melt(id_vars=['zipcode', 'AGI_STUB', 'N1', 'A00100'], value_vars=['N1', 'A00100'], var_name='variable', value_name='value')

# The target schema is ['zipcode', 'AGI_STUB', 'N1', 'A00100']
# The source already has these columns, so no unpivoting of multiple columns is needed.
# The partial plan suggests unpivot then group by zipcode, but since N1 and A00100 are already columns, unpivot is unnecessary.
# Instead, just group by zipcode and AGI_STUB summing N1 and A00100.

result = df.groupby(['zipcode', 'AGI_STUB'], as_index=False)[['N1', 'A00100']].sum()

result = result.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)