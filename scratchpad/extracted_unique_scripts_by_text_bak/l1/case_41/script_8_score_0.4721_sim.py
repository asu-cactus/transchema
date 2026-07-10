import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

id_cols = ['zipcode', 'AGI_STUB', 'N1', 'A00100']
# Columns to keep as id_vars for unpivoting: zipcode, AGI_STUB, N1, A00100 are target columns
# But N1 and A00100 are values to keep, not id_vars. The source has N1 and A00100 as columns.
# The target schema is zipcode, AGI_STUB, N1, A00100
# The source has many columns starting with N and A, but target only wants N1 and A00100.
# So no unpivoting is needed to get only these columns, just select them.

# The partial plan says UNPIVOT, but the target schema is a subset of source columns.
# The source columns N1 and A00100 exist directly.
# So the first operation is to select these columns.

# However, the partial plan says UNPIVOT, so let's check if unpivot is needed.

# The source has many Nxxxx and Axxxx columns, but target only wants N1 and A00100.
# So no unpivoting is needed to get only these columns.

# Therefore, the plan is just to select the columns: zipcode, AGI_STUB, N1, A00100

# Convert columns to integer as target schema says integer

df_result = df[['zipcode', 'AGI_STUB', 'N1', 'A00100']].copy()

df_result = df_result.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)