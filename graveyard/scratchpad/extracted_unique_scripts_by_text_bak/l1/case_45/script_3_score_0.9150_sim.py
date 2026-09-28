import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=["State", "Participation"], 
                       value_vars=["English", "Math", "Reading", "Science", "Composite"],
                       var_name="Subject", value_name="Score")

df0_pivot = df0_unpivot.pivot(index=["State", "Participation"], columns="Subject", values="Score").reset_index()
df0_pivot = df0_pivot.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})

df1_renamed = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

merged = pd.merge(df0_pivot, df1_renamed, on="State", how="inner")

cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_45/target_multisource_mcts.csv", index=False)