import pandas as pd
import hashlib

def incident_type_to_int(s):
    # Normalize string to uppercase and strip spaces for consistent hashing
    s_norm = s.strip().upper()
    return int(hashlib.md5(s_norm.encode('utf-8')).hexdigest()[:8], 16) % (10**8)

def school_year_to_int(s):
    # Extract first 4 digits as year, then subtract 1954 to match target examples
    # e.g. "2014-2015" -> 2014 - 1954 = 60
    try:
        year_start = int(s[:4])
        return year_start - 1954
    except:
        return pd.NA

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    # Normalize column order to standard
    cols = ['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']
    df = df[cols]
    # Convert SCHOOL_YEAR and INCIDENT_TYPE to integers before union
    df['SCHOOL_YEAR'] = df['SCHOOL_YEAR'].astype(str).map(school_year_to_int)
    df['INCIDENT_TYPE'] = df['INCIDENT_TYPE'].astype(str).map(incident_type_to_int)
    dfs.append(df)

# Union all source tables
union_df = pd.concat(dfs, ignore_index=True)

# Group by keys and sum INCIDENT_COUNT
final_grouped = union_df.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], dropna=False, as_index=False)['INCIDENT_COUNT'].sum()

# Cast to integer types matching target schema
final_grouped = final_grouped.astype({
    'ULCS_NO': 'Int64',
    'SCHOOL_YEAR': 'Int64',
    'INCIDENT_TYPE': 'Int64',
    'INCIDENT_COUNT': 'Int64',
    'SCHOOL_ID': 'Int64'
})

final_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)