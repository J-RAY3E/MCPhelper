import asyncio
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import yfinance as yf
from utils.tool_decorator import tool

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import MinMaxScaler
except ImportError:
    LinearRegression = None

class FinancialTools:
    """
    FINANCIAL_TOOLS: Advanced market analysis, technical indicators, 
    forecasting, backtesting, and portfolio analytics.
    """

    @tool()
    def get_stock_info(self, ticker: str) -> str:
        """
        Gets detailed stock information (P/E, market cap, sector, dividend, etc).
        Use this to get fundamentals of any publicly traded company.
        :param ticker: Stock symbol (e.g., 'AAPL', 'MSFT', 'TSLA')
        """
        try:
            stock = yf.Ticker(ticker.strip().upper())
            info = stock.info
            
            if not info or len(info) < 5:
                return f"No information found for '{ticker}'. Verify the ticker symbol."

            fields = [
                'shortName', 'longName', 'sector', 'industry', 'marketCap',
                'priceToBook', 'trailingPE', 'forwardPE', 'dividendYield',
                'beta', '52WeekChange', 'quickRatio', 'currentRatio',
                'debtToEquity', 'profitMargins', 'operatingMargins', 'roe',
                'revenueGrowth', 'earningsGrowth', 'targetMeanPrice',
                'recommendationKey', 'numberOfAnalystOpinions'
            ]
            
            result = f"## 📊 Stock Profile: {ticker.upper()}\n\n"
            
            for field in fields:
                value = info.get(field)
                if value is not None:
                    if field in ['marketCap']:
                        value = f"${value:,.0f}" if value else "N/A"
                    elif field in ['dividendYield', '52WeekChange']:
                        value = f"{value*100:.2f}%" if isinstance(value, (int, float)) else str(value)
                    elif field in ['trailingPE', 'forwardPE', 'priceToBook']:
                        value = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
                    elif isinstance(value, (int, float)) and field in ['beta', 'quickRatio', 'currentRatio', 'profitMargins', 'operatingMargins', 'roe', 'revenueGrowth', 'earningsGrowth']:
                        value = f"{value:.2f}"
                    
                    result += f"**{field}:** {value}\n"
            
            return result
        except Exception as e:
            return f"Error fetching stock info: {str(e)}"

    @tool()
    def get_technical_indicators(self, ticker: str, period: str = "6mo") -> str:
        """
        Calculates technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands.
        Essential for technical analysis and trading decisions.
        :param ticker: Stock symbol (e.g., 'AAPL', 'BTC-USD')
        :param period: Time period - "1mo", "3mo", "6mo", "1y", "2y"
        """
        try:
            ticker = ticker.strip().upper()
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return f"No data found for '{ticker}'"

            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']
            
            indicators = {}
            
            # SMA - Simple Moving Averages
            indicators['SMA_20'] = close.rolling(window=20).mean().iloc[-1]
            indicators['SMA_50'] = close.rolling(window=50).mean().iloc[-1]
            indicators['SMA_200'] = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None
            
            # EMA - Exponential Moving Averages
            indicators['EMA_12'] = close.ewm(span=12, adjust=False).mean().iloc[-1]
            indicators['EMA_26'] = close.ewm(span=26, adjust=False).mean().iloc[-1]
            
            # RSI - Relative Strength Index
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['RSI_14'] = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD
            ema_12 = close.ewm(span=12, adjust=False).mean()
            ema_26 = close.ewm(span=26, adjust=False).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9, adjust=False).mean()
            indicators['MACD'] = macd.iloc[-1]
            indicators['MACD_Signal'] = signal.iloc[-1]
            indicators['MACD_Histogram'] = (macd - signal).iloc[-1]
            
            # Bollinger Bands
            sma_20 = close.rolling(window=20).mean()
            std_20 = close.rolling(window=20).std()
            indicators['BB_Upper'] = (sma_20 + (std_20 * 2)).iloc[-1]
            indicators['BB_Middle'] = sma_20.iloc[-1]
            indicators['BB_Lower'] = (sma_20 - (std_20 * 2)).iloc[-1]
            
            # Average True Range
            high_low = high - low
            high_close = np.abs(high - close.shift())
            low_close = np.abs(low - close.shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            indicators['ATR_14'] = tr.rolling(14).mean().iloc[-1]
            
            # Current price context
            current_price = close.iloc[-1]
            
            result = f"## 📈 Technical Analysis: {ticker}\n"
            result += f"**Current Price:** ${current_price:.2f}\n"
            result += f"**Period:** {period} | Last Updated: {df.index[-1].strftime('%Y-%m-%d')}\n\n"
            
            result += "### Moving Averages\n"
            result += f"- SMA 20: ${indicators['SMA_20']:.2f}\n"
            result += f"- SMA 50: ${indicators['SMA_50']:.2f}\n"
            if indicators['SMA_200']:
                result += f"- SMA 200: ${indicators['SMA_200']:.2f}\n"
            result += f"- EMA 12: ${indicators['EMA_12']:.2f}\n"
            result += f"- EMA 26: ${indicators['EMA_26']:.2f}\n\n"
            
            result += "### Momentum\n"
            result += f"- RSI (14): {indicators['RSI_14']:.2f}\n"
            rsi_val = indicators['RSI_14']
            if rsi_val > 70:
                result += "  → ⚠️ **Overbought** (>70)\n"
            elif rsi_val < 30:
                result += "  → ✅ **Oversold** (<30)\n"
            result += f"- MACD: {indicators['MACD']:.4f}\n"
            result += f"- MACD Signal: {indicators['MACD_Signal']:.4f}\n"
            result += f"- MACD Histogram: {indicators['MACD_Histogram']:.4f}\n\n"
            
            result += "### Bollinger Bands & ATR\n"
            result += f"- Upper Band: ${indicators['BB_Upper']:.2f}\n"
            result += f"- Middle Band: ${indicators['BB_Middle']:.2f}\n"
            result += f"- Lower Band: ${indicators['BB_Lower']:.2f}\n"
            result += f"- ATR (14): ${indicators['ATR_14']:.2f}\n"
            
            # Trend analysis
            result += "\n### 📊 Trend Analysis\n"
            if current_price > indicators['SMA_50']:
                result += "→ Price above SMA50: **BULLISH**\n"
            else:
                result += "→ Price below SMA50: **BEARISH**\n"
            
            if indicators['SMA_50'] > indicators['SMA_200']:
                result += "→ SMA50 > SMA200: **GOLDEN CROSS** (Strong bullish)\n"
            elif indicators['SMA_50'] < indicators['SMA_200']:
                result += "→ SMA50 < SMA200: **DEATH CROSS** (Strong bearish)\n"
            
            if indicators['MACD'] > indicators['MACD_Signal']:
                result += "→ MACD above Signal: **BULLISH MOMENTUM**\n"
            else:
                result += "→ MACD below Signal: **BEARISH MOMENTUM**\n"
            
            return result
            
        except Exception as e:
            return f"Error calculating indicators: {str(e)}"

    @tool()
    def backtest_strategy(self, ticker: str, strategy: str = "sma_crossover", 
                          initial_capital: float = 10000, period: str = "2y") -> str:
        """
        Backtests trading strategies against historical data.
        :param ticker: Stock symbol (e.g., 'AAPL', 'SPY')
        :param strategy: Strategy name - "sma_crossover", "rsi_oversold", "bollinger_bounce"
        :param initial_capital: Starting capital in USD
        :param period: Historical period to test - "1y", "2y", "5y"
        """
        try:
            ticker = ticker.strip().upper()
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                return f"No data found for '{ticker}'"
            
            close = df['Close']
            trades = []
            capital = initial_capital
            shares = 0
            position = None
            
            if strategy == "sma_crossover":
                sma_short = close.rolling(window=20).mean()
                sma_long = close.rolling(window=50).mean()
                
                for i in range(50, len(df)):
                    if sma_short.iloc[i] > sma_long.iloc[i] and position != 'long':
                        if position == 'short':
                            capital = shares * close.iloc[i]
                            shares = 0
                            trades.append(('SELL', df.index[i], close.iloc[i], capital))
                        shares = capital / close.iloc[i]
                        capital = 0
                        position = 'long'
                        trades.append(('BUY', df.index[i], close.iloc[i], shares * close.iloc[i]))
                    elif sma_short.iloc[i] < sma_long.iloc[i] and position == 'long':
                        capital = shares * close.iloc[i]
                        trades.append(('SELL', df.index[i], close.iloc[i], capital))
                        shares = 0
                        position = 'short'
                
                if position == 'long':
                    capital = shares * close.iloc[-1]
            
            elif strategy == "rsi_oversold":
                delta = close.diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))
                
                for i in range(20, len(df)):
                    if rsi.iloc[i] < 30 and position != 'long':
                        if position == 'short':
                            capital = shares * close.iloc[i]
                            shares = 0
                        shares = capital / close.iloc[i]
                        capital = 0
                        position = 'long'
                        trades.append(('BUY', df.index[i], close.iloc[i], 'RSI oversold'))
                    elif rsi.iloc[i] > 70 and position == 'long':
                        capital = shares * close.iloc[i]
                        trades.append(('SELL', df.index[i], close.iloc[i], 'RSI overbought'))
                        shares = 0
                        position = None
                
                if position == 'long':
                    capital = shares * close.iloc[-1]
            
            elif strategy == "bollinger_bounce":
                sma = close.rolling(20).mean()
                std = close.rolling(20).std()
                bb_upper = sma + (std * 2)
                bb_lower = sma - (std * 2)
                
                for i in range(20, len(df)):
                    if close.iloc[i] < bb_lower.iloc[i] and position != 'long':
                        if position == 'short':
                            capital = shares * close.iloc[i]
                            shares = 0
                        shares = capital / close.iloc[i]
                        capital = 0
                        position = 'long'
                        trades.append(('BUY', df.index[i], close.iloc[i], 'BB lower'))
                    elif close.iloc[i] > bb_upper.iloc[i] and position == 'long':
                        capital = shares * close.iloc[i]
                        trades.append(('SELL', df.index[i], close.iloc[i], 'BB upper'))
                        shares = 0
                        position = None
                
                if position == 'long':
                    capital = shares * close.iloc[-1]
            
            total_return = ((capital - initial_capital) / initial_capital) * 100
            num_trades = len(trades)
            
            result = f"## 🔄 Backtest Results: {ticker}\n"
            result += f"**Strategy:** {strategy}\n"
            result += f"**Period:** {period}\n"
            result += f"**Initial Capital:** ${initial_capital:,.2f}\n"
            result += f"**Final Capital:** ${capital:,.2f}\n"
            result += f"**Total Return:** {total_return:.2f}%\n"
            result += f"**Total Trades:** {num_trades}\n\n"
            
            if trades:
                result += "### Trade History (last 10)\n"
                for trade in trades[-10:]:
                    if len(trade) == 4:
                        result += f"- {trade[0]} @ ${trade[2]:.2f} on {trade[1].strftime('%Y-%m-%d')}\n"
                    else:
                        result += f"- {trade[0]} @ ${trade[2]:.2f} ({trade[3]})\n"
            
            # Calculate max drawdown
            if len(trades) > 0:
                equity_curve = [initial_capital]
                for trade in trades:
                    if trade[0] == 'BUY':
                        equity_curve.append(equity_curve[-1])
                    else:
                        equity_curve.append(trade[2])
                
                peak = equity_curve[0]
                max_dd = 0
                for eq in equity_curve:
                    if eq > peak:
                        peak = eq
                    dd = (peak - eq) / peak
                    if dd > max_dd:
                        max_dd = dd
                
                result += f"\n**Max Drawdown:** {max_dd*100:.2f}%\n"
            
            return result
            
        except Exception as e:
            return f"Error running backtest: {str(e)}"

    @tool()
    def forecast_price(self, ticker: str, days: int = 30, period: str = "2y") -> str:
        """
        Advanced Time Series Forecast using Facebook Prophet.
        Includes train-test split for MAPE accuracy evaluation.
        :param ticker: Stock symbol (e.g., 'AAPL', 'BTC-USD')
        :param days: Number of days to forecast into the future
        :param period: Historical data period (default 2y for robust training)
        """
        try:
            from prophet import Prophet
            from sklearn.metrics import mean_absolute_percentage_error
        except ImportError:
            return "Error: prophet and scikit-learn are required for advanced forecasting. Install with: pip install prophet scikit-learn"
        
        try:
            ticker = ticker.strip().upper()
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty or len(df) < 100:
                return f"Insufficient historical data for '{ticker}' to train Prophet. Need at least 100 days."
            
            # Prepare data for Prophet: needs 'ds' (datetime) and 'y' (target)
            df.reset_index(inplace=True)
            # Remove timezone awareness due to Prophet requirement
            df['Date'] = df['Date'].dt.tz_localize(None) 
            prophet_df = df[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
            
            # 1. EVALUATION (Train/Test Split)
            # We withhold the last 30 days to measure real model accuracy
            test_days = min(30, int(len(prophet_df) * 0.1))
            train = prophet_df.iloc[:-test_days]
            test = prophet_df.iloc[-test_days:]
            
            eval_model = Prophet(daily_seasonality=False, yearly_seasonality=True)
            eval_model.fit(train)
            
            future_test = eval_model.make_future_dataframe(periods=test_days)
            forecast_test = eval_model.predict(future_test)
            
            # Extract predictions for the test period
            predictions = forecast_test['yhat'].iloc[-test_days:].values
            actuals = test['y'].values
            
            # Calculate MAPE (Mean Absolute Percentage Error)
            mape = mean_absolute_percentage_error(actuals, predictions) * 100
            
            # 2. ACTUAL FUTURE FORECAST
            # Now train on ALL data to forecast the unknown future
            final_model = Prophet(daily_seasonality=False, yearly_seasonality=True)
            final_model.fit(prophet_df)
            
            future_final = final_model.make_future_dataframe(periods=days)
            # Exclude weekends from future dataframe for stock markets
            future_final = future_final[future_final['ds'].dt.dayofweek < 5]
            
            forecast_final = final_model.predict(future_final)
            
            # Get the future predictions only
            future_predictions = forecast_final.tail(days)
            
            # Prepare output
            result = f"## 🔮 AI Price Forecast: {ticker}\n"
            result += f"**Engine:** Facebook Prophet (Time Series Analysis)\n"
            result += f"**Forecast Period:** {days} trading days\n"
            result += f"**Historical Training Data:** {period}\n\n"
            
            # Accuracy Report
            result += "### 🎯 Model Accuracy (Train/Test Split Test)\n"
            result += f"The model was tested blindly on the last {test_days} days of real data.\n"
            result += f"- **MAPE Error Rate:** {mape:.2f}%\n"
            
            if mape < 5:
                result += "  → ✅ **High Confidence:** The model historically predicts within a 5% error margin.\n"
            elif mape < 15:
                result += "  → ⚠️ **Moderate Confidence:** The model has a 5-15% error margin. Expect variance.\n"
            else:
                result += "  → ❌ **Low Confidence:** The asset is highly volatile. The >15% error margin makes predictions unreliable.\n"
            
            result += "\n### 📈 Future Predictions\n"
            count = 0
            for _, row in future_predictions.iterrows():
                if count < 10 or count == len(future_predictions) - 1:
                    result += f"- {row['ds'].strftime('%Y-%m-%d')}: **${row['yhat']:.2f}** *(Range: ${row['yhat_lower']:.2f} - ${row['yhat_upper']:.2f})*\n"
                elif count == 10:
                    result += f"- ... ({len(future_predictions) - 11} more days)\n"
                count += 1
            
            current_price = df['Close'].iloc[-1]
            predicted_price = future_predictions['yhat'].iloc[-1]
            change_pct = ((predicted_price - current_price) / current_price) * 100
            
            result += f"\n### 📊 Summary\n"
            result += f"**Current Price:** ${current_price:.2f}\n"
            result += f"**Target Price ({days}d):** ${predicted_price:.2f}\n"
            result += f"**Expected Change:** {change_pct:+.2f}%\n"
            
            return result
            
        except Exception as e:
            return f"Error forecasting with Prophet: {str(e)}"

    @tool()
    def get_portfolio_metrics(self, tickers: str, weights: Optional[str] = None) -> str:
        """
        Calculates portfolio metrics: Sharpe ratio, volatility, max drawdown.
        :param tickers: Comma-separated tickers (e.g., 'AAPL,MSFT,GOOG')
        :param weights: Optional comma-separated weights (e.g., '0.4,0.3,0.3')
        """
        try:
            ticker_list = [t.strip().upper() for t in tickers.split(',')]
            
            if weights:
                weight_list = [float(w) for w in weights.split(',')]
                total_weight = sum(weight_list)
                if abs(total_weight - 1.0) > 0.01:
                    weight_list = [w/total_weight for w in weight_list]
            else:
                weight_list = [1.0/len(ticker_list)] * len(ticker_list)
            
            # Fetch data
            data = yf.download(ticker_list, period="1y", progress=False)['Close']
            
            if data.empty:
                return "No data available for provided tickers"
            
            # Handle single ticker case
            if len(ticker_list) == 1:
                returns = data.pct_change().dropna()
            else:
                returns = data.pct_change().dropna()
            
            # Portfolio returns
            if len(ticker_list) > 1:
                portfolio_returns = (returns * weight_list).sum(axis=1)
            else:
                portfolio_returns = returns
            
            # Metrics
            annualized_return = portfolio_returns.mean() * 252
            annualized_vol = portfolio_returns.std() * np.sqrt(252)
            sharpe_ratio = (annualized_return - 0.05) / annualized_vol  # Assuming 5% risk-free rate
            
            # Cumulative returns
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # VaR 95%
            var_95 = portfolio_returns.quantile(0.05) * 100
            
            result = f"## 📊 Portfolio Analysis\n"
            result += f"**Tickers:** {', '.join(ticker_list)}\n"
            result += f"**Weights:** {', '.join([f'{w:.1%}' for w in weight_list])}\n\n"
            
            result += "### Risk Metrics\n"
            result += f"- **Annualized Return:** {annualized_return*100:.2f}%\n"
            result += f"- **Annualized Volatility:** {annualized_vol*100:.2f}%\n"
            result += f"- **Sharpe Ratio:** {sharpe_ratio:.2f}\n"
            result += f"- **Max Drawdown:** {max_drawdown:.2f}%\n"
            result += f"- **VaR (95%):** {var_95:.2f}%\n\n"
            
            # Interpretation
            result += "### Interpretation\n"
            if sharpe_ratio > 1:
                result += "- ✅ **Good Sharpe Ratio** (>1): Good risk-adjusted returns\n"
            elif sharpe_ratio > 0.5:
                result += "- ⚠️ **Moderate Sharpe Ratio** (0.5-1): Acceptable returns\n"
            else:
                result += "- ❌ **Low Sharpe Ratio** (<0.5): Poor risk-adjusted returns\n"
            
            if max_drawdown < -20:
                result += "- ⚠️ **High Drawdown**: Portfolio experienced significant losses\n"
            else:
                result += "- ✅ **Low Drawdown**: Portfolio volatility is controlled\n"
            
            return result
            
        except Exception as e:
            return f"Error calculating portfolio metrics: {str(e)}"

    @tool()
    async def get_sentiment_analysis(self, ticker: str, max_results: int = 10) -> str:
        """
        Analyzes news sentiment for a stock using web scraping.
        :param ticker: Stock symbol (e.g., 'AAPL', 'TSLA')
        :param max_results: Number of news articles to analyze
        """
        try:
            ticker = ticker.strip().upper()
            
            # Fetch news via yfinance
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                # Fallback: search for news
                from core.scraper import LLMFriendlyScraper
                scraper = LLMFriendlyScraper()
                search_url = f"https://news.google.com/search?q={ticker}+stock+news"
                
                result = f"## 📰 Sentiment Analysis: {ticker}\n"
                result += "*(Using web search fallback)*\n\n"
                
                try:
                    pages = await scraper.scrape_multiple([search_url], max_urls=1)
                    if pages:
                        content = pages[0].get('markdown', '')[:2000]
                        result += f"**Latest News Preview:**\n{content}\n"
                except:
                    pass
                
                result += "\n*Unable to fetch detailed news sentiment.*"
                return result
            
            # Analyze sentiment
            headlines = [n.get('title', '') for n in news[:max_results] if n.get('title')]
            
            # Simple keyword-based sentiment
            bullish_keywords = ['surge', 'soar', 'jump', 'gain', 'rise', 'beat', 'upgrade', 'bullish', 'growth', 'profit', 'rally']
            bearish_keywords = ['fall', 'drop', 'plunge', 'crash', 'lose', 'downgrade', 'bearish', 'loss', 'concern', 'fear', 'warning']
            
            bullish_count = 0
            bearish_count = 0
            neutral_count = 0
            
            for headline in headlines:
                head_lower = headline.lower()
                bull = sum(1 for kw in bullish_keywords if kw in head_lower)
                bear = sum(1 for kw in bearish_keywords if kw in head_lower)
                
                if bull > bear:
                    bullish_count += 1
                elif bear > bull:
                    bearish_count += 1
                else:
                    neutral_count += 1
            
            total = len(headlines)
            bullish_pct = (bullish_count / total * 100) if total > 0 else 0
            bearish_pct = (bearish_count / total * 100) if total > 0 else 0
            
            result = f"## 📰 Sentiment Analysis: {ticker}\n"
            result += f"**Articles Analyzed:** {total}\n\n"
            
            result += "### Sentiment Breakdown\n"
            result += f"- 🟢 Bullish: {bullish_count} ({bullish_pct:.0f}%)\n"
            result += f"- 🔴 Bearish: {bearish_count} ({bearish_pct:.0f}%)\n"
            result += f"- ⚪ Neutral: {neutral_count} ({(neutral_count/total*100):.0f}%)\n\n"
            
            # Overall sentiment
            if bullish_pct > 60:
                result += "### Overall: **BULLISH** 📈\n"
            elif bearish_pct > 60:
                result += "### Overall: **BEARISH** 📉\n"
            else:
                result += "### Overall: **MIXED** ⚖️\n"
            
            result += "\n### Recent Headlines\n"
            for i, h in enumerate(headlines[:5], 1):
                result += f"{i}. {h}\n"
            
            return result
            
        except Exception as e:
            return f"Error analyzing sentiment: {str(e)}"

    @tool()
    def get_crypto_data(self, crypto: str, vs_currency: str = "usd", days: int = 30) -> str:
        """
        Gets cryptocurrency data from CoinGecko API (free, no API key needed).
        :param crypto: Crypto symbol (e.g., 'bitcoin', 'ethereum', 'solana')
        :param vs_currency: Currency to compare (usd, eur, etc)
        :param days: Days of historical data
        """
        try:
            # Map common names to CoinGecko IDs
            id_map = {
                'btc': 'bitcoin',
                'bitcoin': 'bitcoin',
                'eth': 'ethereum',
                'ethereum': 'ethereum',
                'sol': 'solana',
                'solana': 'solana',
                'ada': 'cardano',
                'xrp': 'ripple',
                'dot': 'polkadot',
                'doge': 'dogecoin',
                'matic': 'matic-network',
                'avax': 'avalanche-2',
                'link': 'chainlink',
                'uni': 'uniswap'
            }
            
            crypto_id = id_map.get(crypto.lower(), crypto.lower())
            
            # Fetch market data
            url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
            params = {'vs_currency': vs_currency, 'days': days}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return f"CoinGecko API error: {response.status_code}"
            
            data = response.json()
            
            if 'prices' not in data:
                return f"Crypto '{crypto}' not found"
            
            prices = data['prices']
            market_caps = data['market_caps']
            volumes = data['total_volumes']
            
            # Convert to DataFrame
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['market_cap'] = [m[1] for m in market_caps]
            df['volume'] = [v[1] for v in volumes]
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Current values
            current_price = df['price'].iloc[-1]
            price_change_24h = ((df['price'].iloc[-1] - df['price'].iloc[-2]) / df['price'].iloc[-2]) * 100 if len(df) > 1 else 0
            
            # Period stats
            period_high = df['price'].max()
            period_low = df['price'].min()
            period_change = ((current_price - df['price'].iloc[0]) / df['price'].iloc[0]) * 100
            
            result = f"## 💰 Crypto Data: {crypto.upper()}/{vs_currency.upper()}\n"
            result += f"**Period:** {days} days\n\n"
            
            result += "### Current Stats\n"
            result += f"- **Price:** ${current_price:,.4f}\n"
            result += f"- **24h Change:** {price_change_24h:+.2f}%\n"
            result += f"- **Market Cap:** ${df['market_cap'].iloc[-1]:,.0f}\n"
            result += f"- **24h Volume:** ${df['volume'].iloc[-1]:,.0f}\n\n"
            
            result += "### Period Stats\n"
            result += f"- **Period High:** ${period_high:,.4f}\n"
            result += f"- **Period Low:** ${period_low:,.4f}\n"
            result += f"- **Period Change:** {period_change:+.2f}%\n\n"
            
            # Simple moving averages
            df['SMA_7'] = df['price'].rolling(7).mean()
            df['SMA_20'] = df['price'].rolling(20).mean()
            
            if not df['SMA_7'].isna().iloc[-1]:
                result += "### Technical (SMA)\n"
                result += f"- SMA 7: ${df['SMA_7'].iloc[-1]:,.4f}\n"
                result += f"- SMA 20: ${df['SMA_20'].iloc[-1]:,.4f}\n"
                
                if df['SMA_7'].iloc[-1] > df['SMA_20'].iloc[-1]:
                    result += "→ Short MA > Long MA: **BULLISH**\n"
                else:
                    result += "→ Short MA < Long MA: **BEARISH**\n"
            
            return result
            
        except Exception as e:
            return f"Error fetching crypto data: {str(e)}"

    @tool()
    def get_economic_calendar(self, days: int = 7) -> str:
        """
        Gets upcoming economic events and earnings.
        :param days: Number of days to look ahead
        """
        try:
            from datetime import date
            
            # Get major indices for context
            indices = ['^GSPC', '^DJI', '^IXIC']  # S&P500, Dow, Nasdaq
            index_data = []
            
            for idx in indices:
                stock = yf.Ticker(idx)
                hist = stock.history(period="2d")
                if len(hist) >= 2:
                    change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                    name = {'^GSPC': 'S&P 500', '^DJI': 'Dow Jones', '^IXIC': 'Nasdaq'}[idx]
                    index_data.append((name, hist['Close'].iloc[-1], change))
            
            result = f"## 📅 Economic Calendar (Next {days} days)\n\n"
            
            result += "### Market Snapshot\n"
            for name, price, change in index_data:
                emoji = "📈" if change > 0 else "📉"
                result += f"- **{name}:** {emoji} {change:+.2f}%\n"
            
            # Common earnings seasons (approximate)
            today = date.today()
            
            result += "\n### 📊 Earnings Season Indicators\n"
            
            # Q1: Jan-Apr, Q2: Apr-Jul, Q3: Jul-Oct, Q4: Oct-Dec
            month = today.month
            if month in [1, 2, 3, 4]:
                result += "→ Currently: **Q1 Earnings Season** (Banks, Tech early reporters)\n"
            elif month in [5, 6, 7]:
                result += "→ Currently: **Q2 Earnings Season**\n"
            elif month in [8, 9, 10]:
                result += "→ Currently: **Q3 Earnings Season**\n"
            else:
                result += "→ Currently: **Q4 Earnings Season** (Holiday retail, year-end)\n"
            
            # Fed meetings (approximate - typically 8 per year)
            result += "\n### 🏦 Fed Meeting Schedule (2026 - Approximate)\n"
            fed_meetings = [
                "Jan 28-29", "Mar 18-19", "May 6-7", "Jun 17-18",
                "Jul 29-30", "Sep 16-17", "Oct 28-29", "Dec 9-10"
            ]
            result += "FOMC Meeting Dates: " + ", ".join(fed_meetings[:4]) + "...\n"
            
            result += "\n### 💡 Key Metrics to Watch\n"
            result += "- **Non-Farm Payrolls (NFP)** - First Friday of month\n"
            result += "- **CPI (Inflation)** - Mid-month\n"
            result += "- **FOMC Minutes** - 3 weeks after each meeting\n"
            result += "- **GDP Growth** - Quarterly\n"
            result += "- **Earnings Reports** - Quarterly (varies by company)\n"
            
            result += "\n*Note: For real-time calendar data, consider Bloomberg or ForexFactory.*\n"
            
            return result
            
        except Exception as e:
            return f"Error fetching economic calendar: {str(e)}"

    @tool()
    def compare_stocks(self, tickers: str, period: str = "1y") -> str:
        """
        Compares multiple stocks side by side.
        :param tickers: Comma-separated tickers (e.g., 'AAPL,MSFT,GOOG')
        :param period: Comparison period
        """
        try:
            ticker_list = [t.strip().upper() for t in tickers.split(',')]
            
            if len(ticker_list) > 5:
                return "Maximum 5 tickers for comparison"
            
            data = yf.download(ticker_list, period=period, progress=False)['Close']
            
            if data.empty:
                return "No data available"
            
            # Calculate returns
            returns = ((data.iloc[-1] - data.iloc[0]) / data.iloc[0]) * 100
            
            # Volatility
            daily_returns = data.pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100
            
            # Max Drawdown
            cumulative = (1 + daily_returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            max_dd = drawdown.min() * 100
            
            # Correlation matrix
            corr_matrix = daily_returns.corr()
            
            result = f"## 📊 Stock Comparison: {', '.join(ticker_list)}\n"
            result += f"**Period:** {period}\n\n"
            
            result += "### Performance Summary\n"
            result += "| Ticker | Price | Return % | Volatility % | Max DD % |\n"
            result += "|--------|-------|----------|--------------|----------|\n"
            
            for t in ticker_list:
                if t in returns:
                    current = data[t].iloc[-1]
                    ret = returns[t]
                    vol = volatility[t] * 100
                    dd = max_dd.get(t, 0)
                    result += f"| {t} | ${current:.2f} | {ret:+.2f}% | {vol:.2f}% | {dd:.2f}% |\n"
            
            result += "\n### Correlation Matrix\n"
            result += "```\n" + corr_matrix.round(2).to_string() + "```\n"
            
            # Best performer
            best = returns.idxmax()
            worst = returns.idxmin()
            
            result += f"\n### Summary\n"
            result += f"🏆 **Best Performer:** {best} ({returns[best]:+.2f}%)\n"
            result += f"📉 **Worst Performer:** {worst} ({returns[worst]:+.2f}%)\n"
            
            return result
            
        except Exception as e:
            return f"Error comparing stocks: {str(e)}"
