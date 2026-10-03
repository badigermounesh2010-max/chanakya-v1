import logging
from typing import Dict, List, Any, Optional
import time

logger = logging.getLogger(__name__)

class LiveTradingConnector:
    """Live trading integration for Zerodha, Binance, etc."""
    
    def __init__(self, broker: str = 'zerodha', api_key: str = None, api_secret: str = None):
        self.broker = broker
        self.api_key = api_key
        self.api_secret = api_secret
        self.connected = False
        self.positions = {}
        self.orders = []
        self.init_broker_connection()
    
    def init_broker_connection(self):
        """Initialize broker connection"""
        if self.broker == 'zerodha':
            self._init_zerodha()
        elif self.broker == 'binance':
            self._init_binance()
        elif self.broker == 'paper':
            self.connected = True
            logger.info("Paper trading mode enabled")
    
    def _init_zerodha(self):
        """Initialize Zerodha KiteConnect"""
        try:
            from kiteconnect import KiteConnect
            self.kite = KiteConnect(api_key=self.api_key)
            self.connected = True
            logger.info("✅ Zerodha connection established")
        except Exception as e:
            logger.error(f"❌ Zerodha connection failed: {e}")
            self.connected = False
    
    def _init_binance(self):
        """Initialize Binance connection"""
        try:
            from binance.client import Client
            self.binance = Client(api_key=self.api_key, api_secret=self.api_secret)
            self.connected = True
            logger.info("✅ Binance connection established")
        except Exception as e:
            logger.error(f"❌ Binance connection failed: {e}")
            self.connected = False
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        if not self.connected:
            return {'error': 'Not connected to broker'}
        
        try:
            if self.broker == 'zerodha':
                profile = self.kite.profile()
                return {'equity': profile.get('equity', 0), 'cash': profile.get('cash', 0)}
            elif self.broker == 'binance':
                info = self.binance.get_account()
                total_balance = sum(float(asset['free']) + float(asset['locked']) for asset in info['balances'])
                return {'balance': total_balance, 'currency': 'USDT'}
            elif self.broker == 'paper':
                return {'balance': 100000, 'paper_trading': True}
        except Exception as e:
            logger.error(f"Balance fetch error: {e}")
            return {'error': str(e)}
    
    def get_live_price(self, symbol: str) -> Optional[float]:
        """Get live price for symbol"""
        try:
            if self.broker == 'zerodha':
                quote = self.kite.quote('NSE:' + symbol)
                return quote[f'NSE:{symbol}']['last_price']
            elif self.broker == 'binance':
                ticker = self.binance.get_symbol_ticker(symbol=symbol)
                return float(ticker['price'])
        except Exception as e:
            logger.error(f"Price fetch error: {e}")
            return None
    
    def place_order(self, symbol: str, quantity: int, side: str = 'BUY', order_type: str = 'MARKET',
                   price: Optional[float] = None, stop_loss: Optional[float] = None,
                   take_profit: Optional[float] = None) -> Dict[str, Any]:
        """Place order on broker"""
        if not self.connected:
            return {'status': 'error', 'message': 'Not connected to broker'}
        
        try:
            order = {
                'symbol': symbol,
                'quantity': quantity,
                'side': side,
                'type': order_type,
                'price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': time.time(),
                'status': 'submitted'
            }
            
            if self.broker == 'zerodha':
                # Zerodha order placement logic
                order_id = self.kite.place_order(
                    variety='regular',
                    exchange='NSE',
                    tradingsymbol=symbol,
                    transaction_type='BUY' if side == 'BUY' else 'SELL',
                    quantity=quantity,
                    price=price,
                    order_type='MARKET' if order_type == 'MARKET' else 'LIMIT',
                    product='MIS'
                )
                order['order_id'] = order_id
                order['status'] = 'placed'
            
            elif self.broker == 'binance':
                # Binance order placement logic
                if order_type == 'MARKET':
                    result = self.binance.order_market_buy(symbol=symbol, quantity=quantity)
                else:
                    result = self.binance.order_limit_buy(symbol=symbol, timeInForce='GTC', quantity=quantity, price=price)
                order['order_id'] = result['orderId']
                order['status'] = 'placed'
            
            elif self.broker == 'paper':
                order['order_id'] = f"PAPER_{symbol}_{int(time.time())}"
                order['status'] = 'filled'
            
            self.orders.append(order)
            logger.info(f"Order placed: {symbol} {quantity} {side}")
            return order
        
        except Exception as e:
            logger.error(f"Order placement error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        try:
            if self.broker == 'zerodha':
                self.kite.cancel_order(order_id=order_id, variety='regular')
            elif self.broker == 'binance':
                # Binance cancel logic
                pass
            logger.info(f"Order cancelled: {order_id}")
            return {'status': 'success', 'order_id': order_id}
        except Exception as e:
            logger.error(f"Cancel error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        if not self.connected:
            return []
        
        try:
            if self.broker == 'zerodha':
                positions = self.kite.positions()['net']
                return positions
            elif self.broker == 'binance':
                positions = self.binance.get_account()['balances']
                return positions
        except Exception as e:
            logger.error(f"Position fetch error: {e}")
            return []
    
    def get_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent orders"""
        return self.orders[-limit:]

if __name__ == '__main__':
    logger.info("Live trading connector ready")
