import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_1.csv", index_col=0)

result = pd.merge(df1, df0, on="ID", how="inner")

int_cols = ['ID', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu', 'Mjob', 'Fjob', 'reason', 'guardian',
            'traveltime', 'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher',
            'internet', 'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences', 'G1', 'G2', 'G3']

for col in int_cols:
    if col in result.columns:
        if result[col].dtype == 'object':
            result[col] = result[col].map({'M':1, 'F':0, 'yes':1, 'no':0}).fillna(result[col])
        if result[col].dtype == 'object':
            result[col] = pd.to_numeric(result[col], errors='coerce')
        result[col] = result[col].astype('Int64')

result = result[['school'] + int_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_47/target_multisource_mcts.csv", index=False)