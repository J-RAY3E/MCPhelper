# Commands Reference

## Available Commands

### General Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show help and available commands | `/help` |
| Plain text | Ask questions in natural language | "What's the weather?" |

### Data Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/plot [file]` | Create interactive chart from CSV | `/plot data.csv` |
| `/describe [file]` | Show dataset statistics | `/describe sales.csv` |

### Financial Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/info [ticker]` | Company information | `/info AAPL` |
| `/indicators [ticker]` | Technical indicators | `/indicators MSFT` |
| `/backtest [ticker]` | Backtest strategy | `/backtest GOOGL` |
| `/forecast [ticker]` | Price prediction | `/forecast AMZN` |
| `/portfolio [tickers]` | Portfolio metrics | `/portfolio AAPL,MSFT` |
| `/sentiment [ticker]` | News sentiment | `/sentiment TSLA` |
| `/crypto [symbol]` | Crypto data | `/crypto BTC` |
| `/calendar` | Economic calendar | `/calendar` |
| `/compare [tickers]` | Compare stocks | `/compare AAPL,MSFT` |

## Slash Commands

All commands start with `/` and support autocomplete. Type `/` to see available options.

## Output Types

### Text Output
Plain text with Markdown formatting.

### Error Output
Red error messages with error details.

### Mixed Output
Combines text and interactive charts.

### Chart Output
Vega-Lite interactive charts rendered in the UI.
