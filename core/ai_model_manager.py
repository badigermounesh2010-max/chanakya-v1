import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AIModelManager:
    def __init__(self):
        self.groq_client = None
        self.gemini_client = None
        self.openai_client = None
        self.anthropic_client = None
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.ollama_ready = self._check_ollama()
        self._init_clients()

    def _check_ollama(self):
        try:
            import requests
            r = requests.get('http://localhost:11434', timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def _init_clients(self):
        try:
            from groq import Groq
            key = os.getenv('GROQ_API_KEY')
            if key:
                self.groq_client = Groq(api_key=key)
        except Exception as exc:
            logger.warning(f'Groq unavailable: {exc}')

        try:
            import google.generativeai as genai
            key = os.getenv('GOOGLE_API_KEY')
            if key:
                genai.configure(api_key=key)
                self.gemini_client = genai
        except Exception as exc:
            logger.warning(f'Gemini unavailable: {exc}')

        try:
            from openai import OpenAI
            key = os.getenv('OPENAI_API_KEY')
            if key:
                self.openai_client = OpenAI(api_key=key)
        except Exception as exc:
            logger.warning(f'OpenAI unavailable: {exc}')

        try:
            from anthropic import Anthropic
            key = os.getenv('ANTHROPIC_API_KEY')
            if key:
                self.anthropic_client = Anthropic(api_key=key)
        except Exception as exc:
            logger.warning(f'Anthropic unavailable: {exc}')

    async def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        if self.groq_client:
            try:
                res = self.groq_client.chat.completions.create(
                    model='llama3-70b-8192',
                    messages=[{'role': 'user', 'content': prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return res.choices[0].message.content
            except Exception as exc:
                logger.warning(f'Groq generation failed: {exc}')

        if self.gemini_client:
            try:
                model = self.gemini_client.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                return response.text
            except Exception as exc:
                logger.warning(f'Gemini generation failed: {exc}')

        if self.ollama_ready:
            try:
                import requests
                payload = {'model': 'mistral', 'prompt': prompt, 'stream': False, 'temperature': temperature}
                resp = requests.post('http://localhost:11434/api/generate', json=payload, timeout=60)
                data = resp.json()
                return data.get('response', 'Ollama response unavailable')
            except Exception as exc:
                logger.warning(f'Ollama generation failed: {exc}')

        if self.anthropic_client:
            try:
                out = self.anthropic_client.messages.create(
                    model='claude-3-5-sonnet-20241022',
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{'role': 'user', 'content': prompt}],
                )
                return out.content[0].text
            except Exception as exc:
                logger.warning(f'Claude generation failed: {exc}')

        if self.openai_client:
            try:
                comp = self.openai_client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{'role': 'user', 'content': prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return comp.choices[0].message.content
            except Exception as exc:
                logger.warning(f'OpenAI generation failed: {exc}')

        return 'No AI model is available. Add an API key or run Ollama locally.'

    def get_available_models(self):
        return {
            'groq': self.groq_client is not None,
            'gemini': self.gemini_client is not None,
            'openai': self.openai_client is not None,
            'claude': self.anthropic_client is not None,
            'openrouter': bool(self.openrouter_key),
            'ollama_local': self.ollama_ready,
        }
