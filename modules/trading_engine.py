import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class TradingEngine:
    def __init__(self, broker: str = 'zerodha', paper_trading: bool = True):
        self.broker = broker
        self.paper_trading = paper_trading
        self.balance = 100000

    def moving_average_strategy(self, data):
        if len(data) < 2:
            return 0
        close = data['close']
        fast = close.rolling(5).mean().iloc[-1]
        slow = close.rolling(20).mean().iloc[-1]
        if fast > slow:
            return 1
        if fast < slow:
            return -1
        return 0

    def rsi_strategy(self, data, period: int = 14):
        if len(data) < period:
            return 0
        close = data['close']
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, 1e-9)
        rsi = 100 - (100 / (1 + rs))
        if rsi.iloc[-1] < 30:
            return 1
        if rsi.iloc[-1] > 70:
            return -1
        return 0

    def bollinger_bands_strategy(self, data, period: int = 20):
        if len(data) < period:
            return 0
        close = data['close']
        mean = close.rolling(period).mean()
        std = close.rolling(period).std()
        upper = mean + (2 * std)
        lower = mean - (2 * std)
        if close.iloc[-1] < lower.iloc[-1]:
            return 1
        if close.iloc[-1] > upper.iloc[-1]:
            return -1
        return 0

    def backtest_strategy(self, symbol: str, data, strategy_func):
        balance = 100000
        position = 0
        entry_price = 0
        trades = []

        for idx, row in data.iterrows():
            price = float(row['close'])
            signal = strategy_func(data.iloc[:idx + 1])

            if signal == 1 and position == 0:
                position = balance * 0.9 / price
                entry_price = price
            elif signal == -1 and position > 0:
                pnl = (price - entry_price) * position
                balance += pnl
                trades.append({'symbol': symbol, 'entry': entry_price, 'exit': price, 'pnl': pnl})
                position = 0

        return {
            'symbol': symbol,
            'final_balance': balance,
            'num_trades': len(trades),
            'trades': trades,
            'status': 'backtest_complete',
        }

    def place_order(self, symbol: str, quantity: int, side: str = 'buy', price: float | None = None):
        return {
            'status': 'paper_trade_success',
            'symbol': symbol,
            'quantity': quantity,
            'side': side,
            'price': price,
            'paper_trading': self.paper_trading,
        }
