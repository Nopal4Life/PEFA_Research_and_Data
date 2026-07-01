import pandas as pd
from fuzzywuzzy import fuzz


def handle_missing_values(df, action, fill_value=None):
    if action == "Fill":
        df = df.fillna(fill_value)
    elif action == "Drop":
        df = df.dropna()
    # "Keep" -> no-op
    return df


def find_fuzzy_matches(df, columns, threshold=85):
    """Find pairs of similar-looking values within the given columns only.

    Restricting to user-chosen columns (instead of every text column) and
    using a higher default threshold keeps the number of review prompts
    reasonable instead of flooding the user with low-confidence matches.
    """
    matches = []

    for col in columns:
        unique_values = df[col].dropna().unique().tolist()
        for i, val1 in enumerate(unique_values):
            for val2 in unique_values[i + 1:]:
                score = fuzz.ratio(str(val1), str(val2))
                if score >= threshold:
                    matches.append((col, val1, val2, score))

    return matches


def remove_duplicates(df):
    return df.drop_duplicates()
