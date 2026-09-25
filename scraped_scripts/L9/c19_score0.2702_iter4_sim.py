import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

s0_ren = s0.rename(columns={"Certified Units (Millions)": "Certified Units (Millions)"})
s4_ren = s4.rename(columns={"Influenced": "Influenced"})
s5_ren = s5.rename(columns={"Albums in RS500": "Albums in RS500"})
s8_ren = s8.rename(columns={"Times on Cover of RS": "Times on Cover of RS"})
s2_ren = s2.rename(columns={"Spotify": "Spotify"})
s3_ren = s3.rename(columns={"Score": "Score"})

agg = (
    s0_ren.groupby(["Artist"]).agg({"Certified Units (Millions)": "sum"})
    .rename(columns={"Certified Units (Millions)": "Certified Units (Millions)"})
)
agg_influenced = s4_ren.groupby("Artist").agg({"Influenced": "sum"})
agg_albums = s5_ren.groupby("Artist").agg({"Albums in RS500": "sum"})
agg_times_cover = s8_ren.groupby("Artist").agg({"Times on Cover of RS": "sum"})
agg_spotify = s2_ren.groupby("Artist").agg({"Spotify": "sum"})
agg_score = s3_ren.groupby("Artist").agg({"Score": "mean"})

agg_all = (
    agg.join(agg_influenced, how="outer")
    .join(agg_albums, how="outer")
    .join(agg_times_cover, how="outer")
    .join(agg_spotify, how="outer")
    .join(agg_score, how="outer")
    .reset_index()
)

# We need to join agg_all with s7 to get Top 100 Singles and Highest Position
s7_sel = s7[["Artist", "Top 100 Singles", "Highest Position"]].drop_duplicates()
agg_all = agg_all.merge(s7_sel, on="Artist", how="left")

# Now join with s6 to get Years Waited, # of Years Nominated, Inducted By, Year Inducted
s6_sel = s6[["Artist", "Year Inducted", "Years Waited", "# of Years Nominated", "Inducted By"]].drop_duplicates()
df = agg_all.merge(s6_sel, on="Artist", how="left")

# Join with s1 to get Year Inducted, Years Waited, # of Years Nominated (to fill missing if any)
s1_sel = s1[["Artist", "Year Inducted", "Years Waited", "# of Years Nominated"]].drop_duplicates()
df = df.merge(s1_sel, on="Artist", how="left", suffixes=("", "_s1"))

# Fill missing Year Inducted, Years Waited, # of Years Nominated from s1 if missing in s6
df["Year Inducted"] = df["Year Inducted"].combine_first(df["Year Inducted_s1"])
df["Years Waited"] = df["Years Waited"].combine_first(df["Years Waited_s1"])
df["# of Years Nominated"] = df["# of Years Nominated"].combine_first(df["# of Years Nominated_s1"])

df = df.drop(columns=["Year Inducted_s1", "Years Waited_s1", "# of Years Nominated_s1"])

# Reorder and cast columns to target schema and types
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

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)