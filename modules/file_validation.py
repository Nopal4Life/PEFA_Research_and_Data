import pandas as pd

SUPPORTED_EXTENSIONS = (".csv", ".xlsx")


def validate_file(file):
    """Read an uploaded CSV/XLSX into a DataFrame.

    Returns (True, DataFrame) on success or (False, error_message) on failure.
    """
    name = file.name.lower()

    if not name.endswith(SUPPORTED_EXTENSIONS):
        return False, "Unsupported file type. Please upload a CSV or Excel (.xlsx) file."

    try:
        if name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
    except Exception as e:
        return False, f"Error reading file: {e}"

    if df.empty:
        return False, "The uploaded file has no rows."

    return True, df
