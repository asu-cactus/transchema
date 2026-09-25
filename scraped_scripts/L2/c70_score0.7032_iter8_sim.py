import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_70/training_0.csv", index_col=0)

pivot_df = df0.pivot_table(index='school_name', columns='grade', values=['reading_score', 'math_score'], aggfunc='mean')

reading = pivot_df['reading_score']
math = pivot_df['math_score']

avg_scores = (reading + math) / 2

avg_scores = avg_scores.reset_index()

union_df = pd.concat([avg_scores, avg_scores], ignore_index=True)

result = union_df[['school_name', '9th', '10th', '11th', '12th']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_70/target_multisource_mcts.csv", index=False)