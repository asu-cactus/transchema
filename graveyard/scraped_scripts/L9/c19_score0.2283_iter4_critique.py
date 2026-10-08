import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

# Aggregate tables with possible multiple rows per Artist
agg_s0 = s0.groupby("Artist", as_index=False).agg({"Certified Units (Millions)": "sum"})
agg_s4 = s4.groupby("Artist", as_index=False).agg({"Influenced": "sum"})
agg_s5 = s5.groupby("Artist", as_index=False).agg({"Albums in RS500": "sum"})
agg_s8 = s8.groupby("Artist", as_index=False).agg({"Times on Cover of RS": "sum"})
agg_s2 = s2.groupby("Artist", as_index=False).agg({"Spotify": "sum"})
agg_s3 = s3.groupby("Artist", as_index=False).agg({"Score": "mean"})

# Start joining all tables on Artist
df = agg_s0.merge(agg_s4, on="Artist", how="outer")
df = df.merge(agg_s5, on="Artist", how="outer")
df = df.merge(agg_s8, on="Artist", how="outer")
df = df.merge(agg_s2, on="Artist", how="outer")
df = df.merge(agg_s3, on="Artist", how="outer")

# Join with s7 for Top 100 Singles and Highest Position (drop duplicates to avoid duplicates)
s7_sel = s7[["Artist", "Top 100 Singles", "Highest Position"]].drop_duplicates()
df = df.merge(s7_sel, on="Artist", how="outer")

# Join with s6 for Year Inducted, Years Waited, # of Years Nominated, Inducted By (drop duplicates)
s6_sel = s6[["Artist", "Year Inducted", "Years Waited", "# of Years Nominated", "Inducted By"]].drop_duplicates()
df = df.merge(s6_sel, on="Artist", how="outer")

# Join with s1 for Year Inducted, Years Waited, # of Years Nominated to fill missing values (drop duplicates)
s1_sel = s1[["Artist", "Year Inducted", "Years Waited", "# of Years Nominated"]].drop_duplicates()
df = df.merge(s1_sel, on="Artist", how="outer", suffixes=("", "_s1"))

# Fill missing Year Inducted, Years Waited, # of Years Nominated from s1 if missing in s6
df["Year Inducted"] = df["Year Inducted"].combine_first(df["Year Inducted_s1"])
df["Years Waited"] = df["Years Waited"].combine_first(df["Years Waited_s1"])
df["# of Years Nominated"] = df["# of Years Nominated"].combine_first(df["# of Years Nominated_s1"])

df = df.drop(columns=["Year Inducted_s1", "Years Waited_s1", "# of Years Nominated_s1"])

# Reorder columns to match target schema
df = df[
    [
        "Artist",
        "Year Inducted",
        "Years Waited",
        "# of Years Nominated",
        "Inducted By",
        "Influenced",
        "Certified Units (Millions)",
        "Albums in RS500",
        "Top 100 Singles",
        "Highest Position",
        "Times on Cover of RS",
        "Score",
        "Spotify",
    ]
]

# Cast columns to appropriate types
df["Year Inducted"] = pd.to_numeric(df["Year Inducted"], errors="coerce")
df["Years Waited"] = pd.to_numeric(df["Years Waited"], errors="coerce").astype("Int64")
df["# of Years Nominated"] = pd.to_numeric(df["# of Years Nominated"], errors="coerce").astype("Int64")
df["Influenced"] = pd.to_numeric(df["Influenced"], errors="coerce").astype("Int64")
df["Certified Units (Millions)"] = pd.to_numeric(df["Certified Units (Millions)"], errors="coerce")
df["Albums in RS500"] = pd.to_numeric(df["Albums in RS500"], errors="coerce").astype("Int64")
df["Top 100 Singles"] = pd.to_numeric(df["Top 100 Singles"], errors="coerce").astype("Int64")
df["Highest Position"] = pd.to_numeric(df["Highest Position"], errors="coerce").astype("Int64")
df["Times on Cover of RS"] = pd.to_numeric(df["Times on Cover of RS"], errors="coerce").astype("Int64")
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
df["Spotify"] = pd.to_numeric(df["Spotify"], errors="coerce").astype("Int64")

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)