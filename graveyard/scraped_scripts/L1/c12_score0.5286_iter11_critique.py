import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_12/training_1.csv", index_col=0)

# Join Source1_12_0 and Source1_12_1 on Athlete using right join to keep all athletes from Source1_12_1
df_merged = pd.merge(df0, df1, on="Athlete", how="right")

# Fill NaNs in medal and numeric columns with 0 (for athletes without medal info)
for col in ['Age', 'Year', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals']:
    if col in df_merged.columns:
        if df_merged[col].dtype.kind in 'fci':  # float, int, or integer
            df_merged[col] = df_merged[col].fillna(0)

# For Age and Year, fillna(0) is temporary; Age is float, Year is int, but 0 is invalid year/age.
# Instead, keep NaN for Age and Year if no data, or drop rows with missing Age or Year if target examples have none.
# But target examples have no NaNs, so drop rows with missing Age or Year.
df_merged = df_merged.dropna(subset=['Age', 'Year'])

# Cast columns to correct types
df_merged['Age'] = df_merged['Age'].astype(float)
df_merged['Year'] = df_merged['Year'].astype(int)
df_merged['Gold Medals'] = df_merged['Gold Medals'].astype(int)
df_merged['Silver Medals'] = df_merged['Silver Medals'].astype(int)
df_merged['Bronze Medals'] = df_merged['Bronze Medals'].astype(int)
df_merged['Total Medals'] = df_merged['Total Medals'].astype(int)
df_merged['Closing Ceremony Date'] = df_merged['Closing Ceremony Date'].astype(str)
df_merged['Country'] = df_merged['Country'].astype(str)

# Reorder columns to match target schema
df_merged = df_merged[['Athlete', 'Age', 'Year', 'Closing Ceremony Date', 'Gold Medals', 'Silver Medals', 'Bronze Medals', 'Total Medals', 'Country']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_12/target_multisource_mcts.csv", index=False)