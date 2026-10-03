import asyncio
import logging
import os
from datetime import datetime

from dotenv import load_dotenv

from core.ai_model_manager import AIModelManager
from core.ai_systems import SkillSystem, LearningSystem, FeatureLockSystem
from core.database_manager import DatabaseManager
from core.code_generator import CodeGenerator
from core.automation_engine import AutomationEngine
from modules.trading_engine import TradingEngine
from modules.content_engine import ContentEngine
from modules.research_engine import ResearchEngine

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('chanakya')


class ChanakyaApp:
    def __init__(self):
        os.makedirs('data', exist_ok=True)
        self.db = DatabaseManager('data/chanakya.db')
        self.ai_manager = AIModelManager()
        self.skill_system = SkillSystem(self.db)
        self.learning_system = LearningSystem(self.db)
        self.lock_system = FeatureLockSystem(self.db)
        self.code_generator = CodeGenerator(self.ai_manager)
        self.automation = AutomationEngine(delay=0.1)
        self.trader = TradingEngine(broker='zerodha', paper_trading=True)
        self.content_engine = ContentEngine()
        self.research_engine = ResearchEngine(self.ai_manager)
        self.available_models = self.ai_manager.get_available_models()
        logger.info('✅ Chanakya v1 initialized')

    def get_status(self):
        return {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'available_models': self.available_models,
            'skills': self.skill_system.get_all_skills(),
            'feature_status': self.lock_system.locked_features,
        }

    async def generate_code(self, instruction: str):
        return await self.code_generator.generate_code(instruction)

    async def research(self, topic: str, depth: str = 'medium'):
        return await self.research_engine.research_topic(topic, depth)

    async def youtube_script(self, topic: str):
        return await self.content_engine.generate_youtube_script(topic, self.ai_manager)

    def trigger_keyboard(self, text: str):
        self.automation.type_text(text)
        return {'status': 'success', 'text': text}

    def trigger_mouse_click(self, x: int, y: int):
        self.automation.mouse_click(x, y)
        return {'status': 'success', 'x': x, 'y': y}

    def backtest(self, symbol: str, data, strategy_name: str = 'moving_average_strategy'):
        strategy_map = {
            'moving_average_strategy': self.trader.moving_average_strategy,
            'rsi_strategy': self.trader.rsi_strategy,
            'bollinger_bands_strategy': self.trader.bollinger_bands_strategy,
        }
        strategy = strategy_map.get(strategy_name, self.trader.moving_average_strategy)
        return self.trader.backtest_strategy(symbol, data, strategy)


async def main():
    app = ChanakyaApp()
    print('\nChanakya v1 booted successfully\n')
    print(app.get_status())

if __name__ == '__main__':
    asyncio.run(main())
