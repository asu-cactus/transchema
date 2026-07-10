import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True, sort=False)

df['school'] = df['school'].astype(str)
df['ID'] = pd.to_numeric(df['ID'], errors='coerce').astype('Int64')
for col in ['sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu', 'Mjob', 'Fjob', 'reason', 'guardian', 'traveltime', 'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences', 'G1', 'G2', 'G3']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    else:
        df[col] = pd.NA

df = df[['school', 'ID', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu', 'Mjob', 'Fjob', 'reason', 'guardian', 'traveltime', 'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences', 'G1', 'G2', 'G3']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_47/target_multisource_mcts.csv", index=False)