import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_70/training_0.csv", index_col=0)

df0['score'] = (df0['reading_score'] + df0['math_score']) / 2

grouped = df0.groupby(['school_name', 'grade'], as_index=False)['score'].mean()

pivoted = grouped.pivot(index='school_name', columns='grade', values='score')

pivoted = pivoted.rename(columns={'9th': '9th', '10th': '10th', '11th': '11th', '12th': '12th'})

pivoted = pivoted[['10th', '11th', '12th', '9th']]

pivoted.reset_index(inplace=True)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length2_70/target_multisource_mcts.csv", index=False)