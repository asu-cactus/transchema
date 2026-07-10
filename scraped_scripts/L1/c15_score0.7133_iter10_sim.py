import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

union_result = pd.concat([df0, df0], ignore_index=True)
union_result = union_result.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})

df1 = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

merged = pd.merge(union_result, df1, how="inner", on="State")

cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)