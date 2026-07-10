import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_47/training_1.csv", index_col=0)

# Join on 'ID'
merged = pd.merge(df1, df0, on='ID', how='inner')

# Convert categorical columns before aggregation

# Map 'sex' from {'M','F'} to {1,0}
merged['sex'] = merged['sex'].map({'M':1, 'F':0})

# Map 'address' from {'U','R'} to {1,0}
merged['address'] = merged['address'].map({'U':1, 'R':0})

# Map 'famsize' from {'GT3','LE3'} to {1,0}
merged['famsize'] = merged['famsize'].map({'GT3':1, 'LE3':0})

# Map 'Pstatus' from {'T','A'} to {1,0}
merged['Pstatus'] = merged['Pstatus'].map({'T':1, 'A':0})

# For Mjob, Fjob, reason, guardian: factorize to integers
for col in ['Mjob', 'Fjob', 'reason', 'guardian']:
    merged[col] = pd.factorize(merged[col])[0]

# Map binary yes/no columns to 1/0
binary_cols = ['schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic']
for col in binary_cols:
    merged[col] = merged[col].map({'yes':1, 'no':0})

# Convert all other relevant columns to numeric (int)
int_cols = ['age', 'Medu', 'Fedu', 'traveltime', 'studytime', 'failures',
            'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences']
for col in int_cols:
    merged[col] = pd.to_numeric(merged[col], errors='coerce')

# Also convert 'G1', 'G2', 'G3' to numeric
for col in ['G1', 'G2', 'G3']:
    merged[col] = pd.to_numeric(merged[col], errors='coerce')

# Now aggregate all columns except 'school' by mean (no group by)
# For 'school' column, since it's string, take the mode (most frequent)
school_mode = merged['school'].mode()
school_val = school_mode.iloc[0] if not school_mode.empty else ''

# Prepare aggregation dictionary
agg_dict = {}

# Columns to aggregate by mean (all except 'school')
for col in merged.columns:
    if col == 'school':
        continue
    # Only aggregate numeric columns
    if pd.api.types.is_numeric_dtype(merged[col]):
        agg_dict[col] = 'mean'

agg_df = merged.agg(agg_dict).to_frame().T

# Add 'school' column back as mode
agg_df['school'] = school_val

# Reorder columns to match target schema
target_columns = ['school', 'ID', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu',
                  'Mjob', 'Fjob', 'reason', 'guardian', 'traveltime', 'studytime', 'failures',
                  'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet',
                  'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences',
                  'G1', 'G2', 'G3']

# Some columns like Mjob, Fjob, reason, guardian are factorized integers but stored as float after mean aggregation
# Round and convert to int
for col in ['ID', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu',
            'Mjob', 'Fjob', 'reason', 'guardian', 'traveltime', 'studytime', 'failures',
            'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet',
            'romantic', 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences',
            'G1', 'G2', 'G3']:
    agg_df[col] = agg_df[col].round().astype(int)

# Ensure 'school' is string
agg_df['school'] = agg_df['school'].astype(str)

result = agg_df[target_columns]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_47/target_multisource_mcts.csv", index=False)