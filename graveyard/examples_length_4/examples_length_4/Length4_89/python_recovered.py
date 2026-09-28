import pandas as pd

# Define source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length4_89/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_89/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_89/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_89/test_3.csv"
]

# List to hold video series from each source
video_series_list = []

# Load each CSV, extract 'video' column
for file in source_files:
    df = pd.read_csv(file, index_col=0)  # ignore numerical index column
    videos = df['video'].astype(str)       # ensure string dtype
    video_series_list.append(videos)

# Concatenate all video columns vertically
all_videos = pd.concat(video_series_list, axis=0)

# Drop duplicates to have unique videos only
unique_videos = all_videos.drop_duplicates().reset_index(drop=True)

# Convert to DataFrame with column name 'video'
target_df = pd.DataFrame({'video': unique_videos})

# Save to target path
target_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_89/target_multisource_cot.csv", index=False)