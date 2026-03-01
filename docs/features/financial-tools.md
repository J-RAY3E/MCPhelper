# Financial Tools

MCPDESK provides comprehensive financial data and analysis tools.

## Data Sources

- **Yahoo Finance**: Primary data source (no API key required)
- **Alpha Vantage**: Optional, for premium data

## Available Tools

### Stock Information

```bash
/info AAPL
```

Returns:
- Current price
- Market cap
- P/E ratio
- Dividend yield
- 52-week high/low
- Volume
- Company description

### Technical Indicators

```bash
/indicators AAPL
```

Available indicators:
- **SMA**: Simple Moving Average (20, 50, 200)
- **EMA**: Exponential Moving Average
- **RSI**: Relative Strength Index
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**

### Backtesting

```bash
/backtest AAPL
```

Strategy options:
- Moving average crossover
- RSI-based
- Custom parameters

Output:
- Sharpe ratio
- Max drawdown
- Total return
- Win rate

### Price Prediction

```bash
/forecast AAPL
```

Uses ML models to predict:
- 7-day forecast
- 30-day forecast
- Confidence intervals

### Portfolio Analysis

```bash
/portfolio AAPL,MSFT,GOOGL
```

Metrics:
- Sharpe ratio
- Volatility
- Correlation matrix
- Risk assessment

### Sentiment Analysis

```bash
/sentiment TSLA
```

Analyzes:
- Recent news headlines
- Social media sentiment
- Analyst ratings

### Cryptocurrency

```bash
/crypto BTC
/crypto ETH
```

Data:
- Current price
- 24h change
- Volume
- Market cap

### Stock Comparison

```bash
/compare AAPL,MSFT
```

Side-by-side comparison of:
- Price
- P/E ratio
- Growth
- Dividends

## Economic Calendar

```bash
/calendar
```

Shows upcoming:
- Earnings reports
- Economic indicators
- Fed meetings
