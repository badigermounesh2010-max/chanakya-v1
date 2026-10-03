import json
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class ContentEngine:
    def __init__(self):
        self.generated_content = []

    async def generate_youtube_script(self, topic: str, ai_manager) -> Dict:
        prompt = f"Create a high-quality YouTube script for: {topic}. Return JSON with title, description, outline, hashtags, CTA."
        result = await ai_manager.generate_text(prompt, temperature=0.7, max_tokens=2000)
        data = {'topic': topic, 'content': result, 'generated_at': datetime.now().isoformat()}
        self.generated_content.append(data)
        return data

    async def generate_social_post(self, topic: str, platform: str, ai_manager) -> Dict:
        prompt = f"Write a {platform} post about {topic} in a viral style with emoji and hashtags."
        post = await ai_manager.generate_text(prompt, temperature=0.7, max_tokens=500)
        return {'platform': platform, 'topic': topic, 'content': post}
