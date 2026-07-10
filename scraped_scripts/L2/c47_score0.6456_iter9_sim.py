import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on="ID", how="inner")

cols = ['school', 'ID', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu', 'Mjob', 'Fjob', 'reason', 'guardian', 'traveltime', 'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences', 'G1', 'G2', 'G3']

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_47/target_multisource_mcts.csv", index=False)