import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="school_name")

pivoted = merged.pivot_table(index=["school_name", "type"], columns="grade", values=["reading_score", "math_score"], aggfunc="sum")

pivoted.columns = ['_'.join(col).strip() for col in pivoted.columns.values]
pivoted = pivoted.reset_index()

pivoted['a'] = pivoted['type']
pivoted['b'] = pivoted['reading_score_9th'].fillna(0).astype(int)
pivoted['c'] = pivoted['math_score_9th'].fillna(0).astype(int)
pivoted['d'] = pivoted['reading_score_11th'].fillna(0).astype(float)
pivoted['e'] = pivoted['math_score_11th'].fillna(0).astype(float)

result = pivoted[['school_name', 'a', 'b', 'c', 'd', 'e']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)