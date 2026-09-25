import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_70/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_70/training_1.csv", index_col=0)

grouped = df0.groupby(['school_name', 'grade'], as_index=False)['math_score'].mean()

pivoted = grouped.pivot(index='school_name', columns='grade', values='math_score')

pivoted = pivoted.rename_axis(None, axis=1).reset_index()

cols_order = ['school_name', '10th', '11th', '12th', '9th']
for col in cols_order:
    if col not in pivoted.columns:
        pivoted[col] = pd.NA

pivoted = pivoted[cols_order]

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length2_70/target_multisource_mcts.csv", index=False)