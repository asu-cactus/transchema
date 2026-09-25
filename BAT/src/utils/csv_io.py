import pandas as pd


def drop_leading_index_col_if_present(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the first column only if it's actually a throwaway pandas index
    column (unnamed, or literally "Unnamed: 0") -- true for every
    github-pipelines/monteprep-pipelines CSV (hence the previous unconditional
    `.iloc[:, 1:]` at every call site this replaces), but NOT true for
    smart_building's CSVs, whose first column is real data (e.g. CST/date/
    season). Blindly dropping it there would silently corrupt every row --
    the exact same bug already hit and fixed elsewhere for smart_building
    (util/utils.py, ChatGPTwithSQLscript/join_util.py, MMTU/evaluate_autopipeline.py);
    mirrored here for the same reason.
    """
    if len(df.columns) > 0:
        first_col = str(df.columns[0])
        if first_col == "" or first_col.startswith("Unnamed:"):
            return df.drop(columns=df.columns[0])
    return df
