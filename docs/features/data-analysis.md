# Data Analysis

MCPDESK includes built-in data analysis capabilities using pandas and Vega-Lite visualizations.

## Supported Formats

- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)
- JSON (`.json`)
- Parquet (`.parquet`)

## Commands

### /plot

Creates interactive charts from your data.

```bash
/plot mydata.csv
```

Options:
- Column selection: `/plot mydata.csv column=price`
- Chart type: `/plot mydata.csv type=line`
- Group by: `/plot mydata.csv groupby=category`

### /describe

Generates descriptive statistics.

```bash
/describe mydata.csv
```

Output includes:
- Count
- Mean, median, mode
- Standard deviation
- Min, max
- Quartiles

## Charts

### Chart Types

- **Line**: Time series data
- **Bar**: Categorical comparisons
- **Scatter**: Correlation analysis
- **Histogram**: Distribution
- **Box**: Distribution comparison

### Interactive Features

- Zoom and pan
- Tooltips on hover
- Legend toggle
- Export as PNG

## Usage

1. Upload a CSV file via the sidebar
2. Use `/plot filename.csv` to visualize
3. Use `/describe filename.csv` for statistics
