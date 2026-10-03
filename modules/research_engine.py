import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class ResearchEngine:
    def __init__(self, ai_manager):
        self.ai_manager = ai_manager
        self.cache = {}

    async def research_topic(self, topic: str, depth: str = 'medium') -> Dict:
        if topic in self.cache:
            return self.cache[topic]
        prompt = f"Research topic: {topic}. Depth: {depth}. Provide summary, trends, opportunities, risks, and next steps."
        result = await self.ai_manager.generate_text(prompt, temperature=0.5, max_tokens=1800)
        data = {'topic': topic, 'depth': depth, 'content': result, 'generated_at': datetime.now().isoformat()}
        self.cache[topic] = data
        return data
