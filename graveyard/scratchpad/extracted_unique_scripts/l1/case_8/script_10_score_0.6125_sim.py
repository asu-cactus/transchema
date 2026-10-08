import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# JOIN Source1_8_1 and Source1_8_0 on track_id
joined = pd.merge(df1, df0, on="track_id", how="inner")

# UNION Source1_8_0 and Source1_8_1 after aligning columns
df0_for_union = df0.copy()
df0_for_union["index_track"] = pd.NA
df0_for_union = df0_for_union[["index_track", "track_id", "dummy"]]

df1_for_union = df1.copy()
df1_for_union["dummy"] = pd.NA
df1_for_union = df1_for_union[["index_track", "track_id", "dummy"]]

unioned = pd.concat([df0_for_union, df1_for_union], ignore_index=True)

# The target schema is ['index_track', 'track_id', 'dummy']
# The unioned dataframe already has these columns with correct names.
# The joined dataframe has columns: ['index_track', 'track_id', 'dummy']
# But joined has no 'dummy' from df1, so dummy comes from df0.
# The unioned dataframe has dummy or index_track missing per source.

# To produce the final target, we need to fill missing values in unioned:
# For rows from df0, index_track is NA, fill with 0 (or leave as NA? The prompt says fill missing with 0 if needed)
# For rows from df1, dummy is NA, fill with 0

unioned["index_track"] = unioned["index_track"].fillna(0).astype("Int64")
unioned["dummy"] = unioned["dummy"].fillna(0).astype("Int64")
unioned["track_id"] = unioned["track_id"].astype("Int64")

unioned = unioned[["index_track", "track_id", "dummy"]]

unioned.to_csv(target_path, index=False)