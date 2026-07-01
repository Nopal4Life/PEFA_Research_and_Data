# Data Scrapper and Visualizer

A Streamlit app for uploading a CSV/Excel file, cleaning it up, and
visualizing it.

## Features

- Upload a `.csv` or `.xlsx` file
- Preview the data and summary statistics
- Handle missing values (fill, drop, or keep)
- Scan chosen columns for near-duplicate text values (e.g. "NY" vs "N.Y.")
  and review/confirm merges in one batch instead of one prompt at a time
- Remove exact duplicate rows
- Visualize the data: histogram, scatter (with trendline + correlation),
  boxplot, and time series (auto-detects date columns)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Project structure

```
app.py                      # main Streamlit app
modules/
  file_validation.py        # reads/validates the uploaded file
  data_cleaner.py           # missing values, fuzzy-match detection, dedup
  data_visualizer.py        # column type detection + chart builders
```
