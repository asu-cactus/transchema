import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)

# The partial plan suggests joining Source1_9_0 with itself on zipcode and AGI_STUB.
# This is effectively a no-op join since it's the same table joined with itself on the same keys.
# So we can skip the join and directly group by zipcode and AGI_STUB, summing N1 and A00100.

result = df0.groupby(['zipcode', 'AGI_STUB'], as_index=False).agg({'N1':'sum', 'A00100':'sum'})

result = result.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)