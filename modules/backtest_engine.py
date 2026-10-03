import logging
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BacktestEngine:
    """Enterprise-grade backtesting with OHLC data"""
    
    def __init__(self):
        self.results = []
        self.metrics = {}
    
    def load_ohlc_data(self, symbol: str, start_date: str, end_date: str, timeframe: str = '1d') -> pd.DataFrame:
        """Load OHLC data (can integrate with yfinance, ccxt, etc.)"""
        try:
            import yfinance as yf
            data = yf.download(symbol, start=start_date, end=end_date, interval=timeframe)
            return data
        except Exception as e:
            logger.error(f"Failed to load OHLC data: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # SMA
        data['sma_20'] = data['Close'].rolling(20).mean()
        data['sma_50'] = data['Close'].rolling(50).mean()
        data['sma_200'] = data['Close'].rolling(200).mean()
        
        # EMA
        data['ema_12'] = data['Close'].ewm(span=12).mean()
        data['ema_26'] = data['Close'].ewm(span=26).mean()
        
        # MACD
        data['macd'] = data['ema_12'] - data['ema_26']
        data['signal'] = data['macd'].ewm(span=9).mean()
        data['macd_hist'] = data['macd'] - data['signal']
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        bb_sma = data['Close'].rolling(20).mean()
        bb_std = data['Close'].rolling(20).std()
        data['bb_upper'] = bb_sma + (bb_std * 2)
        data['bb_lower'] = bb_sma - (bb_std * 2)
        data['bb_middle'] = bb_sma
        
        # ATR (Average True Range)
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        data['atr'] = true_range.rolling(14).mean()
        
        return data
    
    def backtest(self, symbol: str, data: pd.DataFrame, strategy_func, initial_capital: float = 100000,
                commission: float = 0.001, slippage: float = 0.0001) -> Dict[str, Any]:
        """Run full backtest with OHLC data"""
        
        if len(data) < 50:
            return {'error': 'Insufficient data for backtest'}
        
        # Calculate indicators
        data = self.calculate_indicators(data)
        
        balance = initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity_curve = []
        drawdown_curve = []
        
        max_equity = initial_capital
        
        for idx in range(50, len(data)):
            current_row = data.iloc[idx]
            price = current_row['Close']
            
            # Get signal from strategy
            signal = strategy_func(data.iloc[:idx+1])
            
            # Entry logic
            if signal == 1 and position == 0:
                position = (balance * 0.95) / (price * (1 + slippage))
                entry_price = price * (1 + slippage)
                balance -= position * entry_price * (1 + commission)
            
            # Exit logic
            elif signal == -1 and position > 0:
                exit_price = price * (1 - slippage)
                profit = (exit_price - entry_price) * position
                balance += position * exit_price * (1 - commission)
                
                trades.append({
                    'entry_date': data.index[idx-1],
                    'exit_date': data.index[idx],
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'shares': position,
                    'profit': profit,
                    'profit_pct': (profit / (position * entry_price)) * 100 if position * entry_price > 0 else 0
                })
                position = 0
            
            # Calculate equity
            if position > 0:
                current_equity = balance + (position * price)
            else:
                current_equity = balance
            
            equity_curve.append(current_equity)
            
            # Calculate drawdown
            if current_equity > max_equity:
                max_equity = current_equity
            drawdown = ((max_equity - current_equity) / max_equity) * 100
            drawdown_curve.append(drawdown)
        
        # Close open position
        if position > 0:
            final_price = data.iloc[-1]['Close']
            balance += position * final_price * (1 - commission)
        
        # Calculate metrics
        total_return_pct = ((balance - initial_capital) / initial_capital) * 100
        total_return_usd = balance - initial_capital
        
        winning_trades = [t for t in trades if t['profit'] > 0]
        losing_trades = [t for t in trades if t['profit'] < 0]
        
        win_rate = (len(winning_trades) / len(trades) * 100) if len(trades) > 0 else 0
        
        avg_win = np.mean([t['profit'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['profit'] for t in losing_trades]) if losing_trades else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Sharpe Ratio
        returns = pd.Series(equity_curve).pct_change().dropna()
        sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        # Max Drawdown
        max_dd = max(drawdown_curve) if drawdown_curve else 0
        
        result = {
            'symbol': symbol,
            'strategy': strategy_func.__name__,
            'initial_capital': initial_capital,
            'final_balance': balance,
            'total_return_usd': total_return_usd,
            'total_return_pct': total_return_pct,
            'num_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate_pct': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_dd,
            'trades': trades,
            'equity_curve': equity_curve,
            'drawdown_curve': drawdown_curve,
            'backtest_complete': True
        }
        
        self.results.append(result)
        logger.info(f"Backtest complete: {total_return_pct:.2f}% return, {win_rate:.1f}% win rate")
        return result
    
    def strategy_ma_crossover(self, data: pd.DataFrame) -> int:
        """MA Crossover strategy"""
        if len(data) < 50:
            return 0
        if data['sma_20'].iloc[-1] > data['sma_50'].iloc[-1]:
            return 1
        elif data['sma_20'].iloc[-1] < data['sma_50'].iloc[-1]:
            return -1
        return 0
    
    def strategy_rsi_overbought(self, data: pd.DataFrame) -> int:
        """RSI Overbought/Oversold strategy"""
        if len(data) < 14:
            return 0
        rsi = data['rsi'].iloc[-1]
        if rsi < 30:
            return 1
        elif rsi > 70:
            return -1
        return 0
    
    def strategy_macd(self, data: pd.DataFrame) -> int:
        """MACD strategy"""
        if len(data) < 26:
            return 0
        if data['macd'].iloc[-1] > data['signal'].iloc[-1]:
            return 1
        elif data['macd'].iloc[-1] < data['signal'].iloc[-1]:
            return -1
        return 0
    
    def generate_report(self, result: Dict[str, Any]) -> str:
        """Generate backtest report"""
        report = f"""
╔════════════════════════════════════════╗
║      BACKTEST REPORT - {result['symbol']}              ║
╚════════════════════════════════════════╝

Strategy: {result['strategy']}
Initial Capital: ${result['initial_capital']:,.2f}
Final Balance: ${result['final_balance']:,.2f}
Total Return: ${result['total_return_usd']:,.2f} ({result['total_return_pct']:.2f}%)

Trades Summary:
  Total Trades: {result['num_trades']}
  Winning Trades: {result['winning_trades']}
  Losing Trades: {result['losing_trades']}
  Win Rate: {result['win_rate_pct']:.2f}%

Profitability:
  Avg Win: ${result['avg_win']:.2f}
  Avg Loss: ${result['avg_loss']:.2f}
  Profit Factor: {result['profit_factor']:.2f}

Risk Metrics:
  Sharpe Ratio: {result['sharpe_ratio']:.2f}
  Max Drawdown: {result['max_drawdown_pct']:.2f}%
"""
        return report

if __name__ == '__main__':
    logger.info("Backtest engine ready")
