import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_1.csv", index_col=0)

# Join on ID
df = pd.merge(df1, df0, on="ID")

# Map yes/no to 1/0
mapping_yes_no = {"yes": 1, "no": 0}
mapping_sex = {"M": 1, "F": 0}

df["sex"] = df["sex"].map(mapping_sex)
df["schoolsup"] = df["schoolsup"].map(mapping_yes_no)
df["famsup"] = df["famsup"].map(mapping_yes_no)
df["paid"] = df["paid"].map(mapping_yes_no)
df["activities"] = df["activities"].map(mapping_yes_no)
df["nursery"] = df["nursery"].map(mapping_yes_no)
df["higher"] = df["higher"].map(mapping_yes_no)
df["internet"] = df["internet"].map(mapping_yes_no)
df["romantic"] = df["romantic"].map(mapping_yes_no)

# Convert categorical columns to codes
for col in ["Mjob", "Fjob", "reason", "guardian", "address", "famsize", "Pstatus"]:
    df[col] = df[col].astype('category').cat.codes

# Define columns to convert to int
int_cols = ['ID', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu', 'Mjob', 'Fjob', 'reason', 'guardian',
            'traveltime', 'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher',
            'internet', 'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences', 'G1', 'G2', 'G3']

df = df.astype({col: 'int64' for col in int_cols if col in df.columns})

# Group by 'school' and sum all other columns
agg_dict = {col: 'sum' for col in df.columns if col != 'school'}
df = df.groupby('school', as_index=False).agg(agg_dict)

# Reorder columns to match target schema
target_cols = ['school', 'ID', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu', 'Mjob', 'Fjob', 'reason',
               'guardian', 'traveltime', 'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'activities', 'nursery',
               'higher', 'internet', 'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences',
               'G1', 'G2', 'G3']

df = df[target_cols]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length2_47/target_multisource_mcts.csv", index=False)