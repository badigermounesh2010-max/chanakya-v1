from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
import asyncio
import os
from datetime import datetime

logger = logging.getLogger(__name__)

def create_dashboard_app(chanakya_app):
    """Create Flask dashboard app"""
    app = Flask(__name__, template_folder='dashboard/templates', static_folder='dashboard/static')
    CORS(app)
    
    # ===== API Routes =====
    
    @app.route('/api/status', methods=['GET'])
    def api_status():
        """Get app status"""
        return jsonify(chanakya_app.get_status())
    
    @app.route('/api/models', methods=['GET'])
    def api_models():
        """Get available AI models"""
        return jsonify(chanakya_app.available_models)
    
    @app.route('/api/trades', methods=['GET'])
    def api_trades():
        """Get trade history"""
        limit = request.args.get('limit', 50, type=int)
        trades = chanakya_app.db.get_trades(limit)
        return jsonify({'trades': [dict(zip(['id', 'symbol', 'entry', 'exit', 'qty', 'side', 'pnl', 'status', 'created', 'closed'], t)) for t in trades]})
    
    @app.route('/api/skills', methods=['GET'])
    def api_skills():
        """Get AI skills"""
        return jsonify(chanakya_app.skill_system.get_all_skills())
    
    @app.route('/api/code/generate', methods=['POST'])
    def api_generate_code():
        """Generate code"""
        data = request.json
        instruction = data.get('instruction', '')
        result = asyncio.run(chanakya_app.generate_code(instruction))
        return jsonify(result)
    
    @app.route('/api/trading/backtest', methods=['POST'])
    def api_backtest():
        """Run backtest"""
        data = request.json
        symbol = data.get('symbol', 'NIFTY')
        strategy = data.get('strategy', 'moving_average_strategy')
        # This requires OHLC data - would need to load it first
        return jsonify({'status': 'backtest_endpoint_ready'})
    
    @app.route('/api/automation/mouse', methods=['POST'])
    def api_mouse():
        """Control mouse"""
        data = request.json
        x = data.get('x', 0)
        y = data.get('y', 0)
        chanakya_app.trigger_mouse_click(x, y)
        return jsonify({'status': 'success', 'action': 'mouse_click'})
    
    @app.route('/api/automation/keyboard', methods=['POST'])
    def api_keyboard():
        """Control keyboard"""
        data = request.json
        text = data.get('text', '')
        chanakya_app.trigger_keyboard(text)
        return jsonify({'status': 'success', 'action': 'keyboard_type'})
    
    @app.route('/api/research', methods=['POST'])
    def api_research():
        """Research a topic"""
        data = request.json
        topic = data.get('topic', '')
        depth = data.get('depth', 'medium')
        result = asyncio.run(chanakya_app.research(topic, depth))
        return jsonify(result)
    
    @app.route('/api/youtube', methods=['POST'])
    def api_youtube():
        """Generate YouTube script"""
        data = request.json
        topic = data.get('topic', '')
        result = asyncio.run(chanakya_app.youtube_script(topic))
        return jsonify(result)
    
    # ===== HTML Routes =====
    
    @app.route('/')
    def dashboard():
        """Main dashboard"""
        return render_template('index.html')
    
    @app.route('/trading')
    def trading():
        """Trading dashboard"""
        return render_template('trading.html')
    
    @app.route('/automation')
    def automation():
        """Automation dashboard"""
        return render_template('automation.html')
    
    @app.route('/ai')
    def ai():
        """AI dashboard"""
        return render_template('ai.html')
    
    return app

if __name__ == '__main__':
    logger.info("Flask dashboard app factory ready")
